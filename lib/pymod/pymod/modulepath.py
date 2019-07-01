import os
import re
from six import StringIO

import pymod.alias
import pymod.names
import pymod.module
from pymod.discover import find_modules

from contrib.util import groupby, join, split

import llnl.util.tty as tty
from llnl.util.lang import Singleton
from llnl.util.tty.color import colorize
from llnl.util.tty.colify import colified


class Path:
    def __init__(self, dirname):
        self.path = dirname
        self.modules = find_modules(dirname)


class Modulepath:
    def __init__(self, directories):
        self.path = []
        for directory in directories:
            path = Path(directory)
            if not path.modules:
                continue
            self.path.append(path)
        self.defaults = {}
        self.assign_defaults()

    def __contains__(self, dirname):
        return dirname in [p.path for p in self.path]

    def __iter__(self):
        return iter(self.path)

    def walk(self, start=0):
        assert start >= 0
        for path in self.path[start:]:
            yield path

    def __len__(self):
        return len(self.path)

    def index(self, dirname):
        for (i, path) in enumerate(self.path):
            if path.path == dirname:
                return i
        raise ValueError('{0} not in Modulepath'.format(dirname))  # pragma: no cover

    def clear(self):
        for path in self.path[::-1]:
            self.remove_path(path.path)

    @property
    def value(self):
        if not self.path:
            return None
        return join([p.path for p in self.path], os.pathsep)

    def _get(self, key):
        """Implementation of `get`"""
        if os.path.isdir(key) and key in self:
            return self.getby_dirname(key)
        if os.path.isfile(key):
            module = self.getby_filename(key)
            if module is not None:
                module.acquired_as = module.filename
            return module
        parts = key.split(os.path.sep)
        if len(parts) == 1:
            # with length of 1, it must be a name
            module = self.defaults.get(key)
            if module is not None:
                module.acquired_as = module.name
            return module
        else:
            for path in self.path:
                for module in path.modules:
                    if module.fullname == key:
                        module.acquired_as = key
                        return module
                    elif module.endswith(key):
                        module.acquired_as = key
                        return module
        return None

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
        module = self._get(key)
        if module is None:
            # Module has not been found.  Try an alias
            target = pymod.alias.get(key)
            if target is not None:
                if target['modulepath'] not in self.path:
                    tty.warn('Alias {0} points to {1}, but {1} is not on the '
                             'current MODULEPATH.  Use {2} to make {1} available'
                             .format(key, target['target'], target['modulepath'])
                            )
                module = self.get(target['filename'])
        return module

    def getby_dirname(self, dirname):
        for path in self:
            if path.path == dirname:
                return path.modules

    def getby_filename(self, filename):
        for path in self.path:
            for module in path.modules:
                if filename == module.filename:
                    return module
        return None

    def path_modified(self):
        self.assign_defaults()

    def append_path(self, dirname):
        if dirname in self:
            return
        path = Path(dirname)
        if not path.modules:
            return
        self.path.append(path)
        self.path_modified()
        return path.modules

    def prepend_path(self, dirname):
        if dirname in self:
            path = self.path.pop(self.index(dirname))
        else:
            path = Path(dirname)
            if not path.modules:
                return None
        self.path.insert(0, path)
        self.path_modified()
        return path.modules

    def remove_path(self, dirname):
        """Remove `dirname` from the modulepath

        Parameters
        ----------
        dirname : str
            The directory to remove

        Returns
        -------
        modules_in_dir : list of Module
            The modules in the directory that was removed

        """

        if dirname not in self:  # pragma: no cover
            tty.warn('Modulepath: {0!r} is not in modulepath'.format(dirname))
            return []

        modules_in_dir = self.getby_dirname(dirname)
        self.path.pop(self.index(dirname))
        self.path_modified()

        return modules_in_dir

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
            modules = [m for m in modules if re.search(regex, m.fullname)]
        return modules

    def colorize(self, string):
        """Colorize item for output to console"""
        D = '(%s)' % colorize('@R{D}')
        L = '(%s)' % colorize('@G{L}')
        DL = '(%s,%s)' % (colorize('@R{D}'), colorize('@G{L}'))
        colorized = string.replace('(D)', D)
        colorized = colorized.replace('(L)', L)
        colorized = colorized.replace('(D,L)', DL)
        return colorized

    @staticmethod
    def sort_key(module):
        return (module.name, module.version)

    def avail(self, terse=False, regex=None):

        sio = StringIO()
        if not terse:
            _, width = tty.terminal_size()
            head = lambda x: (' ' + x + ' ').center(width, '-')
            for path in self:
                directory = path.path
                modules = path.modules
                modules = sorted([m for m in modules if m.is_enabled], key=self.sort_key)
                modules = self.filter_modules_by_regex(modules, regex)
                if not os.path.isdir(directory):  # pragma: no cover
                    s = colorize('@r{(Directory not readable)}'.center(width))
                elif not modules:  # pragma: no cover
                    if regex:
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
                if not modules:  # pragma: no cover
                    continue
                sio.write(directory + ':\n')
                sio.write('\n'.join(m.fullname for m in modules))
            sio.write('\n')

        description = sio.getvalue()

        return description

    def candidates(self, key):
        # Return a list of modules that might by given by key
        the_candidates = []
        for path in self:
            if not path.modules:  # pragma: no cover
                continue
            for module in path.modules:
                if module.name.endswith(key):
                    the_candidates.append(module)  # pragma: no cover
                elif module.fullname.endswith(key):
                    the_candidates.append(module)  # pragma: no cover
                else:
                    f = module.filename
                    if not isinstance(module, pymod.module.TclModule):
                        f = os.path.splitext(f)[0]
                    if f.endswith(key):  # pragma: no cover
                        the_candidates.append(module)
        return the_candidates


def _modulepath():  # pragma: no cover
    path = split(os.getenv(pymod.names.modulepath), os.pathsep)
    return Modulepath(path)


_path = Singleton(_modulepath)


def path():
    return [p.path for p in _path.path]


def set_path(other_path):
    global _path
    _path = other_path


def get(key):
    return _path.get(key)


def append_path(dirname):
    return _path.append_path(dirname)


def remove_path(dirname):
    return _path.remove_path(dirname)


def prepend_path(dirname):
    return _path.prepend_path(dirname)


def avail(**kwargs):
    return _path.avail(**kwargs)


def candidates(name):
    return _path.candidates(name)


def contains(path):
    return path in _path


def walk(start=0):
    return _path.walk(start=0)


def size():
    return len(_path)


def clear():
    return _path.clear()
