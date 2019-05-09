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


class Modulepath:
    def __init__(self, directories):
        self.path = []
        self.modules = []
        self.db = {'by_name': {}}
        self._modified = False
        self._grouped_by_modulepath = None
        self.set_path(directories)

    def export_env(self):
        env = dict()
        if self._modified:
            key = pymod.names.modulepath
            value = join(self.path, os.pathsep)
            env.update({key: value})
        return env

    def __contains__(self, dirname):
        return dirname in self.path

    def get(self, key):
        """Get a module from the available modules.

        """
        if isinstance(key, pymod.module.Module):
            return key
        if os.path.isdir(key) and key in self.path:
            return self.getby_dirname(key)
        if os.path.isfile(key):
            return self.getby_filename(key)
        parts = key.split(os.path.sep)
        if len(parts) == 1:
            return self.getby_name(key)
        if len(parts) == 2:
            return self.getby_fullname(key)
        return None

    def getby_dirname(self, dirname):
        return [m for m in self.modules if m.modulepath == dirname]

    def getby_name(self, name):
        return self.db['by_name'].get(name)

    def getby_fullname(self, fullname):
        for (_, modules) in self.group_by_modulepath():
            for module in modules:
                if module.fullname == fullname:
                    return module
        return None

    def getby_filename(self, filename):
        for (_, modules) in self.group_by_modulepath():
            for module in modules:
                if module.filename == filename:
                    return module
        return None

    def _path_modified(self):
        self._grouped_by_modulepath = None
        self.assign_defaults()
        self._modified = True

    def append_path(self, dirname):
        if not os.path.isdir(dirname):
            tty.warn('Modulepath: {0!r} is not a directory'.format(dirname))
        if dirname in self.path:
            return
        modules_in_dir = find_modules(dirname)
        if not modules_in_dir:
            tty.warn('Modulepath: no modules found in {0}'.format(dirname))
            return
        self.modules.extend(modules_in_dir)
        self.path.append(dirname)
        self._path_modified()
        return modules_in_dir

    def prepend_path(self, dirname):
        if not os.path.isdir(dirname):
            tty.warn('Modulepath: {0!r} is not a directory'.format(dirname))
            return [], []
        if dirname in self.path:
            self.path.pop(self.path.index(dirname))
            modules_in_dir = [m for m in self.modules
                              if m.modulepath == dirname]
        else:
            modules_in_dir = find_modules(dirname)
            if not modules_in_dir:
                tty.warn('Modulepath: no modules found in {0}'.format(dirname))
                return [], []
            self.modules.extend(modules_in_dir)
        self.path.insert(0, dirname)
        self._path_modified()

        # Determine which modules changed in priority due to insertion of new
        # directory in to path
        bumped = []
        grouped_by_modulepath = self.group_by_modulepath()
        fullnames = [m.fullname for m in grouped_by_modulepath[0][1]]
        for (_, modules) in grouped_by_modulepath[1:]:
            for module in modules:
                if module.fullname in fullnames:
                    bumped.append(module)
        return modules_in_dir, bumped

    def remove_path(self, dirname):
        modules_in_dir, orphaned, bumped = [], [], []

        if dirname not in self.path:
            tty.warn('Modulepath: {0!r} is not in modulepath'.format(dirname))
            return modules_in_dir, orphaned, bumped

        modules_in_dir.extend(self.getby_dirname(dirname))
        orphaned.extend([m for m in modules_in_dir if m.is_loaded])
        self.modules = [m for m in self.modules if m not in modules_in_dir]
        self.path.pop(self.path.index(dirname))
        self._path_modified()

        # Determine which modules may have moved up in priority due to removal
        # of directory from path
        for orphan in orphaned:
            other = self.getby_fullname(orphan.fullname)
            if other is not None:
                bumped.append(other)
                continue
            other = self.getby_name(orphan.name)
            if other is not None:
                bumped.append(other)
                continue
            bumped.append(None)
        tty.debug(str(orphaned))
        return modules_in_dir, orphaned, bumped

    def set_path(self, directories):
        self.path = []
        self.modules = []
        if not directories:
            return
        for directory in directories:
            if not os.path.isdir(directory):
                tty.verbose(
                    'Modulepath: nonexistent directory {0!r}'.format(directory))
                continue
            modules_in_dir = find_modules(directory)
            if not modules_in_dir:
                tty.verbose(
                    'Modulepath: no modules found in {0}'.format(directory))
                continue
            self.modules.extend(modules_in_dir)
            self.path.append(directory)
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
            return 0
        self.db['by_name'] = {}
        for (_, modules) in groupby(self.modules, lambda x: x.name):
            for module in modules:
                module.is_default = False
            if len(modules) > 1:
                modules = sorted(modules,
                                 key=cmp_to_key(compare_module_versions),
                                 reverse=True)
                modules[0].is_default = True
            self.db['by_name'][modules[0].name] = modules[0]

    def group_by_modulepath(self, sort=False):
        if self._grouped_by_modulepath is None:
            grouped = dict(groupby(self.modules, lambda x: x.modulepath))
            self._grouped_by_modulepath = []
            for dirname in self.path:
                if sort:
                    modules = sorted(grouped.pop(dirname), key=lambda m: m.fullname)
                else:
                    modules = grouped.pop(dirname)
                self._grouped_by_modulepath.append((dirname, modules))
        return self._grouped_by_modulepath

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
            for (directory, modules) in self.group_by_modulepath():
                modules = sorted([m for m in modules if m.is_enabled], key=self.sort_key)
                if not os.path.isdir(directory):
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
            for (directory, modules) in self.group_by_modulepath():
                if not os.path.isdir(directory):
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

    def apply(self, fun):
        for (_, modules) in self.group_by_modulepath():
            for module in modules:
                fun(module)

    def candidates(self, key):
        # Return a list of modules that might by given by key
        the_candidates = set()
        regex = re.compile(key)
        for (_, modules) in self.group_by_modulepath():
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
