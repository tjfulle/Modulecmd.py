import os
import re
from six import StringIO

import pymod.module
from pymod.modulepath.discover import find_modules

from contrib.util import groupby
import llnl.util.tty as tty
from contrib.util import join
from contrib.util.tty import grep_pat_in_string
from llnl.util.tty.color import colorize
from llnl.util.tty.colify import colified


class Path:
    def __init__(self, dirname):
        self.path = dirname
        self.modules = find_modules(dirname)
        if not self.modules: # pragma: no cover
            tty.verbose('Path: no modules found in {0}'.format(dirname))


class Modulepath:
    def __init__(self, directories):
        self.clear()
        self.set_path(directories)

    def clear(self):
        self.path = []
        self.defaults = {}
        self._modified = False

    def __contains__(self, dirname):
        return dirname in [p.path for p in self.path]

    def __iter__(self):
        return iter(self.path)

    def __len__(self):
        return len(self.path)

    def index(self, dirname):
        for (i, path) in enumerate(self.path):
            if path.path == dirname:
                return i
        raise ValueError('{0} not in Modulepath'.format(dirname))

    def get(self, key):
        """Get a module from the available modules using the following rules:

        If `key`:

            1. is a Module, just return it;
            2. is a directory, return all of the modules in that directory;
            3. is a file name, return the module pointed to by the name;
            4. is a module name (with no version info), return the default
               version; and
            5. meets none of the above criteria, the best match will be
               returned. The best match is found by looking through all
               MODULEPATH directories and returning the first module whose
               filename ends with `key`.

        """
        if isinstance(key, pymod.module.Module):
            return key
        elif os.path.isdir(key) and key in self:
            return self.getby_dirname(key)
        if os.path.isfile(key):
            return self.getby_filename(key)
        parts = key.split(os.path.sep)
        if len(parts) == 1:
            # with length of 1, it must be a name
            return self.defaults.get(key)
        else:
            for path in self.path:
                for module in path.modules:
                    if module.fullname == key:
                        return module
                    elif module.endswith(key):
                        return module
        return None

    def getby_dirname(self, dirname):
        for path in self:
            if path.path == dirname:
                return path.modules
        return []

    def getby_filename(self, filename):
        for path in self.path:
            for module in path.modules:
                if filename == module.filename:
                    return module
        return None

    def _path_modified(self):
        self.assign_defaults()
        self._modified = True

    def append_path(self, dirname):
        if not os.path.isdir(dirname):  # pragma: no cover
            tty.warn('Modulepath: {0!r} is not a directory'.format(dirname))
        if dirname in self:
            return
        path = Path(dirname)
        if not path.modules:
            return
        self.path.append(path)
        self._path_modified()
        return path.modules

    def prepend_path(self, dirname):
        if not os.path.isdir(dirname):  # pragma: no cover
            tty.warn('Modulepath: {0!r} is not a directory'.format(dirname))
            return [], []
        if dirname in self:
            path = self.path.pop(self.index(dirname))
        else:
            path = Path(dirname)
            if not path.modules:
                return [], []
        self.path.insert(0, path)
        self._path_modified()

        # Determine which modules changed in priority due to insertion of new
        # directory in to path
        lost_precedence = []
        fullnames = [m.fullname for m in self.path[0].modules]
        for p in self.path[1:]:
            for module in p.modules:
                if module.fullname in fullnames:
                    lost_precedence.append(module)
        return path.modules, lost_precedence

    def remove_path(self, dirname):
        modules_in_dir, orphaned, gained_precedence = [], [], []

        if dirname not in self:  # pragma: no cover
            tty.warn('Modulepath: {0!r} is not in modulepath'.format(dirname))
            return modules_in_dir, orphaned, gained_precedence

        modules_in_dir.extend(self.getby_dirname(dirname))
        orphaned.extend([m for m in modules_in_dir if m.is_loaded])
        self.path.pop(self.index(dirname))
        self._path_modified()

        # Determine which modules may have moved up in priority due to removal
        # of directory from path
        for orphan in orphaned:
            other = self.get(orphan.fullname)
            if other is not None:
                gained_precedence.append(other)
                continue
            other = self.defaults.get(orphan.name)
            if other is not None:
                gained_precedence.append(other)
                continue
            gained_precedence.append(None)
        return modules_in_dir, orphaned, gained_precedence

    def set_path(self, directories):
        self.path = []
        if not directories:
            return
        for directory in directories:
            if not os.path.isdir(directory):  # pragma: no cover
                tty.verbose(
                    'Modulepath: nonexistent directory {0!r}'.format(directory))
                continue
            path = Path(directory)
            if not path.modules:
                tty.verbose(
                    'Modulepath: no modules found in {0}'.format(directory))
                continue
            self.path.append(path)
        self._path_modified()

    def assign_defaults(self):
        """Assign defaults to modules.
        1. Look for an exact match in all MODULEPATH directories. Pick the
           first match.
        2. If the name doesn't contain a version, look for a marked default in
           the first directory that has one.
        3. Look for the Highest version in all MODULEPATH directories. If there
           are two or more modulefiles with the Highest version then the first one
           in MODULEPATH order will be picked.

        Given a module with multiple versions, the default is the module with
        the highest version across all modules, unless explicitly made the
        default. A module is explicitly made the default by creating a symlink
        to it (in the same directory) named 'default'
        """
        def module_default_sort_key(module):
            sort_key = (1 if module.marked_as_default else -1,
                        module.version,
                        module.variant,
                        -self.index(module.modulepath))
            return sort_key
        self.defaults = {}
        grouped = groupby(
            [module for path in self.path for module in path.modules],
            lambda x: x.name)
        for (_, modules) in grouped:
            for module in modules:
                module.is_default = False
            if len(modules) > 1:
                modules = sorted(modules,
                                 key=module_default_sort_key,
                                 reverse=True)
                modules[0].is_default = True
            self.defaults[modules[0].name] = modules[0]

    def filter_modules_by_regex(self, modules, regex):
        if regex:
            modules = [m for m in modules if re.search(regex, m.name)]
        return modules

    def colorize(self, string):
        """Colorize item for output to console"""
        D = '(' + colorize('@g{D}') + ')'
        L = '(' + colorize('@m{L}') + ')'
        DL = '(' + colorize('@g{D}') + ',' + colorize('@m{L}') + ')'
        colorized = string.replace('(D)', D)
        colorized = colorized.replace('(L)', L)
        colorized = colorized.replace('(D,L)', DL)
        return colorized

    @staticmethod
    def sort_key(module):
        return (module.name, module.version)

    def export_env(self):
        env = dict()
        if self._modified:
            key = pymod.names.modulepath
            value = join([p.path for p in self.path], os.pathsep)
            env.update({key: value})
        return env

    def format_available(self, terse=False, regex=None, fulloutput=False):

        sio = StringIO()
        if not terse:
            _, width = tty.terminal_size()
            head = lambda x: (' ' + x + ' ').center(width, '-')
            for path in self:
                directory = path.path
                modules = path.modules
                modules = sorted([m for m in modules if m.is_enabled], key=self.sort_key)
                if not os.path.isdir(directory):  # pragma: no cover
                    if not fulloutput:
                        continue
                    s = colorize('@r{(Directory does not exist)}'.center(width))
                elif not modules:
                    if not fulloutput:  # pragma: no cover
                        continue
                    s = colorize('@r{(None)}'.center(width))
                else:
                    s = colified([m.format_info() for m in modules], width=width)
                    s = self.colorize(s)
                directory = directory.replace(os.path.expanduser('~/'), '~/')
                sio.write(head(directory) + '\n')
                sio.write(s + '\n')
        else:
            for path in self:
                directory = path.path
                modules = path.modules
                if not os.path.isdir(directory):  # pragma: no cover
                    continue
                modules = sorted([m for m in modules if m.is_enabled], key=self.sort_key)
                modules = self.filter_modules_by_regex(modules, regex)
                if not modules:
                    continue
                sio.write(directory + ':\n')
                sio.write('\n'.join(m.fullname for m in modules))
            sio.write('\n')

        description = sio.getvalue()
        if regex is not None:
            description = grep_pat_in_string(description, regex)

        return description

    def candidates(self, key):
        # Return a list of modules that might by given by key
        the_candidates = set()
        regex = re.compile(key)
        for path in self:
            modules = path.modules
            if not modules:
                continue
            for module in modules:
                if regex.search(module.filename):
                    the_candidates.add(module.fullname)
                elif regex.search(module.name) and module.is_default:
                    the_candidates.add(module.fullname)
                elif regex.search(module.fullname):
                    the_candidates.add(module.fullname)
        return sorted(list(the_candidates))
