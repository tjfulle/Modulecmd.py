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
from contrib.functools_backport import cmp_to_key


class Path:
    def __init__(self, dirname):
        self.path = dirname
        self.modules = find_modules(dirname)
        if not self.modules:
            tty.verbose('Path: no modules found in {0}'.format(dirname))

    def __contains__(self, key):
        if isinstance(key, pymod.module.Module):
            return key in self.modules
        if os.path.isfile(key):
            return key in self.filenames
        parts = key.split(os.path.sep)
        if len(parts) == 1:
            return key in self.names
        if len(parts) == 2:
            return key in self.fullnames

    @property
    def filenames(self):
        return [m.filename for m in self.modules]

    @property
    def names(self):
        return [m.name for m in self.modules]

    @property
    def fullnames(self):
        return [m.fullname for m in self.modules]

    def getby_name(self, name):
        for module in self.modules:
            if module.name == name:
                return module
        return None

    def getby_fullname(self, fullname):
        for module in self.modules:
            if module.fullname == fullname:
                return module
        return None

    def getby_filename(self, filename):
        for module in self.modules:
            if module.filename == filename:
                return module
        return None


class Modulepath:
    def __init__(self, directories):
        self.path = []
        self.defaults = {}
        self._modified = False
        self.set_path(directories)

    def export_env(self):
        env = dict()
        if self._modified:
            key = pymod.names.modulepath
            value = join([p.path for p in self.path], os.pathsep)
            env.update({key: value})
        return env

    def __contains__(self, dirname):
        return dirname in [p.path for p in self.path]

    def __iter__(self):
        return iter(self.path)

    def __len__(self):
        return len(self.path)

    def get(self, key):
        """Get a module from the available modules.

        """
        if isinstance(key, pymod.module.Module):
            return key
        if os.path.isdir(key) and key in self:
            return self.getby_dirname(key)
        if os.path.isfile(key):
            return self.getby_filename(key)
        parts = key.split(os.path.sep)
        if len(parts) == 1:
            return self.getby_name(key)
        if len(parts) == 2:
            return self.getby_fullname(key)
        return None

    def index(self, dirname):
        for (i, path) in enumerate(self.path):
            if path.path == dirname:
                return i
        raise ValueError('{0} not in Modulepath'.format(dirname))

    def getby_dirname(self, dirname):
        for path in self:
            if path.path == dirname:
                return path.modules
        return []

    def getby_name(self, name):
        return self.defaults.get(name)

    def getby_fullname(self, fullname):
        for path in self.path:
            module = path.getby_fullname(fullname)
            if module is not None:
                return module
        return None

    def getby_filename(self, filename):
        for path in self.path:
            module = path.getby_filename(filename)
            if module is not None:
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

        if dirname not in self:
            tty.warn('Modulepath: {0!r} is not in modulepath'.format(dirname))
            return modules_in_dir, orphaned, gained_precedence

        modules_in_dir.extend(self.getby_dirname(dirname))
        orphaned.extend([m for m in modules_in_dir if m.is_loaded])
        self.path.pop(self.index(dirname))
        self._path_modified()

        # Determine which modules may have moved up in priority due to removal
        # of directory from path
        for orphan in orphaned:
            other = self.getby_fullname(orphan.fullname)
            if other is not None:
                gained_precedence.append(other)
                continue
            other = self.getby_name(orphan.name)
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
        """Assign defaults to modules.  Given a module with multiple versions,
        the default is the module with the highest version across all modules,
        unless explicitly made the default.  A module is explicitly made the
        default by creating a symlink to it (in the same directory) named
        'default'"""
        def compare_module_versions(a, b):
            if a.is_explicit_default:
                return 1
            elif b.is_explicit_default:
                return -1
            elif a.version > b.version:
                return 1
            elif b.version > a.version:
                return -1
            ai = self.index(a.modulepath)
            bi = self.index(b.modulepath)
            if ai < bi:
                return 1
            elif bi < ai:
                return -1
            raise ValueError(  # pragma: no cover
                "This is a state of module version comparison that should "
                "never be reached.  Please inform the Modulecmd.py developers")
        self.defaults = {}
        grouped = groupby(
            [module for path in self.path for module in path.modules],
            lambda x: x.name)
        for (_, modules) in grouped:
            for module in modules:
                module.is_default = False
            if len(modules) > 1:
                modules = sorted(modules,
                                 key=cmp_to_key(compare_module_versions),
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
                    if not fulloutput:
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
