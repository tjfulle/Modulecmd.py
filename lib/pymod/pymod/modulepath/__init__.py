import os
import re

from pymod.modulepath.discover import find_modules
import pymod.module

from contrib.util.itertools import groupby
from contrib.util.lang import Singleton
import contrib.util.logging as logging
import contrib.util.misc as misc
from contrib.util.logging.color import colorize
from contrib.util.logging.colify import colified
from contrib.functools_backport import cmp_to_key


class Modulepath:
    def __init__(self, directories):
        self.path = []
        self.modules = []
        self.db = {}
        self._grouped_by_modulepath = None
        self.set_path(directories)

    def __contains__(self, path):
        return path in self.path

    def get(self, key):
        """Get a module from the available modules.

        """
        if os.path.isfile(key):
            return self.getby_filename(key)
        parts = key.split(os.path.sep)
        if len(parts) == 1:
            return self.getby_name(key)
        if len(parts) == 2:
            return self.getby_fullname(key)

    def getby_filename(self, filename):
        for module in self.modules:
            if module.filename == path:
                return module
        return None

    def getby_name(self, name):
        return self.db['by_name'].get(name)

    def getby_fullname(self, fullname):
        for (_, modules) in self.group_by_modulepath():
            for module in modules:
                if module.fullname == fullname:
                    return module
        return None

    def _path_modified(self):
        self._grouped_by_modulepath = None
        self.assign_defaults()

    def append_path(self, dirname):
        if not os.path.isdir(dirname):
            logging.warn(
                'Modulepath: {0!r} is not a directory'.format(dirname))
        if dirname in self.path:
            return
        modules_in_dir = find_modules(dirname)
        if not modules_in_dir:
            logging.warn(
                'Modulepath: no modules found in {0}'.format(dirname))
            return
        self.modules.extend(modules_in_dir)
        self.path.append(dirname)
        self._path_modified()
        return modules_in_dir

    def prepend_path(self, dirname):
        if not os.path.isdir(dirname):
            logging.warn(
                'Modulepath: {0!r} is not a directory'.format(dirname))
        if dirname in self.path:
            self.path.pop(self.path.index(dirname))
            modules_in_dir = [m for m in self.modules if m.modulepath == dirname]
        else:
            modules_in_dir = find_modules(dirname)
            if not modules_in_dir:
                logging.warn(
                    'Modulepath: no modules found in {0}'.format(dirname))
                return
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
        if dirname not in self.path:
            logging.warn(
                'Modulepath: {0!r} is not in modulepath'.format(dirname))
            return
        removed = []
        for (i, module) in enumerate(self.modules):
            if module.modulepath == dirname:
                removed.append(module)
                self.modules[i] = None
        self.modules = [m for m in self.modules if m is not None]
        self.path.pop(self.path.index(dirname))
        self._path_modified()

        # Determine which modules may have moved up in priority due to removed
        # of directory from path
        bumped = []
        fullnames = [m.fullname for m in removed]
        for (_, modules) in self.group_by_modulepath():
            for module in modules:
                if module.fullname in fullnames:
                    bumped.append(module)
        return removed, bumped

    def set_path(self, directories):
        self.path = []
        self.modules = []
        if not directories:
            return
        for directory in directories:
            if not os.path.isdir(directory):
                logging.verbose(
                    'Modulepath: nonexistent directory {0!r}'.format(directory))
                continue
            modules_in_dir = find_modules(directory)
            if not modules_in_dir:
                logging.verbose(
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

    def format_available(self, terse=False, regex=None, fulloutput=False, pathonly=False):
        if pathonly:
            return '\n'.join('{0}) {1}'.format(i,_[0]) for i,_ in enumerate(self, start=1))

        description = []
        if not terse:
            _, width = logging.terminal_size()
            for (directory, modules) in self.group_by_modulepath():
                modules = [m for m in modules if m.is_enabled]
                modules = self.filter_modules_by_regex(modules, regex)
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
                description.append((' ' + directory + ' ').center(width, '-'))
                description.append(s + '\n')
        else:
            for (directory, modules) in self.group_by_modulepath():
                if not os.path.isdir(directory):
                    continue
                modules = self.filter_modules_by_regex(modules, regex)
                if not modules:
                    continue
                description.append(directory + ':')
                description.append('\n'.join(m.fullname for m in modules))
            description.append('')

        description = '\n'.join(description)
        if regex is not None:
            description = misc.grep_pat_in_string(description, regex)

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


def _path():
    path = misc.split(os.getenv(pymod.names.modulepath), os.pathsep)
    return Modulepath(path)


path = Singleton(_path)


def set_path(other_path):
    global path
    path = other_path


def group_by_modulepath():
    return path.group_by_modulepath()


def get(key):
    return path.get(key)


def append_path(dirname):
    return path.append_path(dirname)


def remove_path(dirname):
    return path.remove_path(dirname)


def prepend_path(dirname):
    return path.prepend_path(dirname)


def format_available(**kwargs):
    return path.format_available(**kwargs)
