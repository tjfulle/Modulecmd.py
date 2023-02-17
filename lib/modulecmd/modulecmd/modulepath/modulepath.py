import os
import re
import bisect
from six import StringIO
from types import SimpleNamespace
from collections import OrderedDict as ordered_dict

import modulecmd.alias
import modulecmd.names
import modulecmd.module
from modulecmd.modulepath.path import Path
from modulecmd._util import expand_string

from modulecmd.util.lang import join
from modulecmd.util.itertools import groupby

import llnl.util.tty as tty
from llnl.util.tty.color import colorize
from llnl.util.tty.colify import colified


class Modulepath:
    def __init__(self, directories):
        self.path = ordered_dict()
        for directory in directories:
            path = Path(directory)
            if not path.modules:
                continue
            self.path[path.path] = path.modules
        self.defaults = {}
        self.assign_defaults()

    def __contains__(self, dirname):
        return dirname in self.path

    def __iter__(self):
        for (dirname, modules) in self.path.items():
            yield SimpleNamespace(path=dirname, modules=modules)

    def __len__(self):
        return len(self.path)

    def size(self):
        return len(self)

    def clear(self):
        paths = list(reversed(self.path))
        for path in paths:
            self.remove_path(path)

    @property
    def value(self):
        if not self.path:
            return None
        return join(list(self.path.keys()), os.pathsep)

    def _get(self, key, use_file_modulepath=False):
        """Implementation of `get`"""
        tty.debug(key)
        if os.path.isdir(key) and key in self:
            return self.getby_dirname(key)
        if os.path.isfile(key):
            tty.debug(key)
            module = self.getby_filename(key, use_file_modulepath=use_file_modulepath)
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
            for (path, modules) in self.path.items():
                for module in modules:
                    if module.fullname == key:
                        module.acquired_as = key
                        return module
                    elif module.endswith(key):
                        module.acquired_as = key
                        return module
        return None

    def get(self, key, use_file_modulepath=False):
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
        module = self._get(key, use_file_modulepath=use_file_modulepath)
        if module is None:
            # Module has not been found.  Try an alias
            target = modulecmd.alias.get(key)
            if target is not None:
                # It does no harm to append the alias's modulepath. If it is
                # already used, append_path is a null op, it is not already
                # being used, then appending has less side effects than
                # prepending.
                self.append_path(target["modulepath"])
                module = self.getby_filename(target["filename"])
                if module is None:  # pragma: no cover
                    tty.warn(
                        "Alias {0} points to nonexistent target {1}".format(
                            key, target["target"]
                        )
                    )
        return module

    def getby_dirname(self, dirname):
        for path in self:
            if path.path == dirname:
                return path.modules

    def getby_filename(self, filename, use_file_modulepath=False):
        tty.debug(filename)
        filename = os.path.abspath(filename)
        for (path, modules) in self.path.items():
            tty.debug(path)
            for module in modules:
                if filename == module.filename:
                    return module

        if not use_file_modulepath:
            return None

        # This file is not on the MODULEPATH, add it
        modules = self.append_path(os.path.dirname(filename))
        for module in modules:
            if filename == module.filename:
                return module

        # Hmmmm, how did we get this far???
        return None

    def path_modified(self):
        self.assign_defaults()

    def append_path(self, dirname):
        dirname = Path.expand_name(dirname)
        if dirname in self:
            return
        path = Path(dirname)
        if not path.modules:
            tty.verbose("No modules found in {0}".format(path.path))
            return
        self.path[path.path] = path.modules
        self.path_modified()
        return path.modules

    def prepend_path(self, dirname):
        dirname = Path.expand_name(dirname)
        modules = self.path.get(dirname)
        if modules is None:
            path = Path(dirname)
            if not path.modules:
                return None
            self.path[path.path] = path.modules
            self.path.move_to_end(path.path, last=False)
            modules = path.modules
        else:
            self.path.move_to_end(dirname, last=False)
        self.path_modified()
        return modules

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
        dirname = Path.expand_name(dirname)
        if dirname not in self:  # pragma: no cover
            tty.warn("Modulepath: {0!r} is not in modulepath".format(dirname))
            return []

        modules_in_dir = self.getby_dirname(dirname)
        self.path.pop(dirname, None)
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
            n = list(self.path.keys()).index(module.modulepath)
            sort_key = (
                1 if module.marked_as_default else -1,
                module.version,
                module.variant,
                -n,
            )
            return sort_key

        self.defaults = {}
        grouped = groupby([m for _ in self.path.values() for m in _], lambda x: x.name)
        for (_, modules) in grouped:
            for module in modules:
                module.is_default = False
            if len(modules) > 1:
                modules = sorted(modules, key=module_default_sort_key, reverse=True)
                modules[0].is_default = True
            self.defaults[modules[0].name] = modules[0]

    def filter_modules_by_regex(self, modules, regex):
        if regex:
            modules = [m for m in modules if re.search(regex, m.fullname)]
        return modules

    def colorize(self, string):
        """Colorize item for output to console"""
        D = "(%s)" % colorize("@R{D}")
        L = "(%s)" % colorize("@G{L}")
        DL = "(%s,%s)" % (colorize("@R{D}"), colorize("@G{L}"))
        colorized = string.replace("(D)", D)
        colorized = colorized.replace("(L)", L)
        colorized = colorized.replace("(D,L)", DL)
        return colorized

    @staticmethod
    def sort_key(module):
        return (module.name, module.version)

    def avail(self, terse=False, regex=None, long_format=False):
        if terse:
            return self.avail_terse(regex=regex)
        else:
            return self.avail_full(regex=regex, long_format=long_format)

    def avail_full(self, regex=None, long_format=False):
        sio = StringIO()
        sio.write("\n")
        _, width = tty.terminal_size()
        # head = lambda x: (" " + x + " ").center(width, "-")
        for path in self:
            directory = path.path
            modules = sorted(
                [m for m in path.modules if m.is_enabled], key=self.sort_key
            )
            modules = self.filter_modules_by_regex(modules, regex)
            if not os.path.isdir(directory):  # pragma: no cover
                s = colorize("@r{(Directory not readable)}".center(width))
            elif not modules:  # pragma: no cover
                if regex:
                    continue
                s = colorize("@r{(None)}".center(width))
            else:
                modules = [self.colorize(m.format_dl_status()) for m in modules]
                aliases = modulecmd.alias.get(directory)
                if aliases:  # pragma: no cover
                    for (alias, target) in aliases:
                        i = bisect.bisect_left(modules, alias)
                        insert_key = colorize("@M{%s}@@" % (alias))
                        if long_format:  # pragma: no cover
                            insert_key += " -> %s" % (target)
                        modules.insert(i, insert_key)
                s = colified(modules, width=width)
            directory = directory.replace(os.path.expanduser("~/"), "~/")
            # sio.write(head(directory) + '\n')
            sio.write(colorize("@G{%s}:\n" % (directory)))
            sio.write(s + "\n")
        return sio.getvalue()

    def avail_terse(self, regex=None):
        sio = StringIO()
        for path in self:
            directory = path.path
            modules = path.modules
            if not os.path.isdir(directory):  # pragma: no cover
                continue
            modules = sorted([m for m in modules if m.is_enabled], key=self.sort_key)
            modules = self.filter_modules_by_regex(modules, regex)
            if not modules:  # pragma: no cover
                continue
            sio.write(directory + ":\n")
            sio.write("\n".join(m.fullname for m in modules))
        sio.write("\n")
        return sio.getvalue()

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
                    if not isinstance(module, modulecmd.module.TclModule):
                        f = os.path.splitext(f)[0]
                    if f.endswith(key):  # pragma: no cover
                        the_candidates.append(module)
        return the_candidates
