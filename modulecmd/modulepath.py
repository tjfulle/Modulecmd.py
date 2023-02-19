import os
import re
import sys
import bisect
from string import Template
from collections import OrderedDict as ordered_dict


import modulecmd.xio as xio
import modulecmd.cache
import modulecmd.alias
import modulecmd.names
import modulecmd.module
import modulecmd.util as util


def expand_name(dirname: str) -> None:
    return os.path.expanduser(Template(dirname).safe_substitute(**os.environ))


class Modulepath:
    def __init__(self, path: str = None, sep: str = None) -> None:
        sep = sep or os.pathsep
        path = path or os.getenv("MODULEPATH", "")
        if isinstance(path, str):
            path = [_.strip() for _ in path.split(sep) if _.split()]
        path = util.unique(
            expand_name(p) for p in path if util.isreadable(p, os.path.isdir)
        )
        self.populate(path)
        self.defaults = {}
        self.assign_global_defaults()

    def populate(self, path):
        self.path = ordered_dict()
        for p in path:
            if p == "/":
                xio.warn("requested to search / for modules, skipping")
                continue
            modules = find_modules(p)
            if modules:
                self.path[p] = modules

    def __contains__(self, dirname):
        return dirname in self.path

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
        return util.join(list(self.path.keys()), os.pathsep)

    def _get(self, key, use_file_modulepath=False):
        """Implementation of `get`"""
        xio.debug(key)
        if os.path.isdir(key) and key in self:
            return self.getby_dirname(key)
        if os.path.isfile(key):
            xio.debug(key)
            module = self.getby_filename(key, use_file_modulepath=use_file_modulepath)
            if module is not None:
                module.acquired_as = module.file
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
                    xio.warn(
                        "Alias {0} points to nonexistent target {1}".format(
                            key, target["target"]
                        )
                    )
        return module

    def getby_dirname(self, dirname):
        for (path, modules) in self.path.items():
            if path == dirname:
                return modules

    def getby_filename(self, filename, use_file_modulepath=False):
        xio.debug(filename)
        filename = os.path.abspath(filename)
        for (path, modules) in self.path.items():
            xio.debug(path)
            for module in modules:
                if filename == module.file:
                    return module

        if not use_file_modulepath:
            return None

        # This file is not on the MODULEPATH, add it
        modules = self.append_path(os.path.dirname(filename))
        for module in modules:
            if filename == module.file:
                return module

        # Hmmmm, how did we get this far???
        return None

    def path_modified(self):
        self.assign_global_defaults()

    def append_path(self, dirname):
        dirname = expand_name(dirname)
        if dirname in self:
            return
        modules = find_modules(dirname)
        if not modules:
            xio.verbose(f"No modules found in {dirname}")
            return
        self.path[dirname] = modules
        self.path_modified()
        return modules

    def prepend_path(self, dirname):
        dirname = expand_name(dirname)
        modules = self.path.get(dirname)
        if modules is not None:
            self.path.move_to_end(dirname, last=False)
        else:
            modules = find_modules(dirname)
            if not modules:
                return None
            self.path[dirname] = modules
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
        dirname = expand_name(dirname)
        if dirname not in self.path:  # pragma: no cover
            xio.warn("Modulepath: {0!r} is not in modulepath".format(dirname))
            return []

        modules_in_dir = self.getby_dirname(dirname)
        self.path.pop(dirname, None)
        self.path_modified()

        return modules_in_dir

    def assign_global_defaults(self):
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

        def sort_key(module):
            n = list(self.path.keys()).index(module.modulepath)
            return (1 if module.is_explicit_default else -1, module.version, -n)

        self.defaults = {}
        grouped = util.groupby(
            [m for _ in self.path.values() for m in _], lambda x: x.name
        )
        for (name, modules) in grouped:
            for module in modules:
                module.is_global_default = None
            if len(modules) > 1:
                modules = sorted(modules, key=sort_key, reverse=True)
                modules[0].is_global_default = True
            self.defaults[modules[0].name] = modules[0]

    def filter_modules_by_regex(self, modules, regex):
        if regex:
            modules = [m for m in modules if re.search(regex, m.fullname)]
        return modules

    @staticmethod
    def sort_key(module):
        return (module.name, module.version)

    def format_avail(self, terse=False, regex=None, long_format=False, file=None):
        if terse:
            return self.format_avail_terse(regex=regex, file=file)
        else:
            return self.format_avail_full(
                regex=regex, long_format=long_format, file=file
            )

    def format_avail_full(self, regex=None, long_format=False, file=None):
        file = file or sys.stdout
        file.write("\n")
        width = util.terminal_size().columns
        # head = lambda x: (" " + x + " ").center(width, "-")
        for (directory, modules) in self.path.items():
            modules = sorted([m for m in modules if m.is_enabled], key=self.sort_key)
            modules = self.filter_modules_by_regex(modules, regex)
            if not os.path.isdir(directory):  # pragma: no cover
                s = util.colorize("{red}(Directory not readable){endc}".center(width))
            elif not modules:  # pragma: no cover
                if regex:
                    continue
                s = util.colorize("{red}(None){endc}".center(width))
            else:
                names = []
                for module in modules:
                    name = module.fullname
                    stat = []
                    if module.is_default:
                        stat.append(util.colorize("{bold}{red}D{endc}"))
                    if module.is_loaded:
                        stat.append(util.colorize("{bold}{green}L{endc}"))
                    if stat:
                        name += f" ({','.join(stat)})"
                    names.append(name)
                aliases = modulecmd.alias.get(directory)
                if aliases:  # pragma: no cover
                    for (alias, target) in aliases:
                        i = bisect.bisect_left(names, alias)
                        insert_key = util.colorize("{magenta}%s{endc}@" % alias)
                        if long_format:  # pragma: no cover
                            insert_key += " -> %s" % (target)
                        names.insert(i, insert_key)
                s = util.colify(names, width=width) + "\n"
            directory = directory.replace(os.path.expanduser("~/"), "~/")
            file.write(util.colorize("{green}%s{endc}:\n" % directory))
            file.write(s + "\n")
        return

    def format_avail_terse(self, regex=None, file=None):
        file = file or sys.stdout
        for (directory, modules) in self.path.items():
            if not os.path.isdir(directory):  # pragma: no cover
                continue
            modules = sorted([m for m in modules if m.is_enabled], key=self.sort_key)
            modules = self.filter_modules_by_regex(modules, regex)
            if not modules:  # pragma: no cover
                continue
            file.write(directory + ":\n")
            file.write("\n".join(m.fullname for m in modules))
        file.write("\n")
        return

    def candidates(self, key):
        # Return a list of modules that might by given by key
        the_candidates = []
        for modules in self.path.values():
            if not modules:  # pragma: no cover
                continue
            for module in modules:
                if module.name.endswith(key):
                    the_candidates.append(module)  # pragma: no cover
                elif module.fullname.endswith(key):
                    the_candidates.append(module)  # pragma: no cover
                else:
                    f = module.file
                    if not isinstance(module, modulecmd.module.TclModule):
                        f = os.path.splitext(f)[0]
                    if f.endswith(key):  # pragma: no cover
                        the_candidates.append(module)
        return the_candidates


marked_default_names = ("default", ".version")
skip_dirs = (".git", ".svn", "CVS")


def find_modules(root, branch=None):
    cached_modules = get_cached_modules(root)
    if cached_modules is not None:
        return cached_modules
    modules = []
    if root == "/":
        xio.verbose("Requesting to find modules in root directory")
        return None
    elif not os.path.isdir(root):
        xio.verbose("{root!r} is not a directory")
        return None
    elif os.path.basename(root) in skip_dirs:  # pragma: no cover
        return None
    with util.working_dir(root):
        for p in os.listdir(branch or "."):
            if modulecmd.module.ishidden(p):
                continue
            f = os.path.normpath(os.path.join(branch or ".", p))
            if modulecmd.module.ismodule(f):
                m = modulecmd.module.factory(root, f)
                if m.is_enabled:
                    modules.append(m)
            elif os.path.isdir(f):
                modules.extend(find_modules(root, branch=f) or [])
    modules = sorted(modules, key=lambda m: (m.name, m.version))
    if branch is None:
        cache_modules(root, modules)
    return modules


def listdir(dirname):
    files, dirs = [], []
    if not os.access(dirname, os.X_OK):  # pragma: no cover
        return [], []
    with util.working_dir(dirname):
        for item in os.listdir("."):
            if os.path.isdir(item):
                if item in (".git", ".svn", "CVS"):  # pragma: no cover
                    continue
                dirs.append(item)
            else:
                files.append(item)
    return files, dirs


def isfilelike(item):
    return os.path.exists(item) and not os.path.isdir(item)


def get_cached_modules(path):
    if not modulecmd.config.get("use_modulepath_cache"):  # pragma: no cover
        return None
    section = modulecmd.names.modulepath
    cached = modulecmd.cache.get(section, path)
    if cached is None:
        return None

    modules = [modulecmd.module.from_dict(m) for m in cached]
    if any([m is None for m in modules]):
        # A module was removed, the cache is invalid
        modulecmd.cache.pop(section, path)
        return None
    return modules


def cache_modules(path, modules):
    if not modulecmd.config.get("use_modulepath_cache"):  # pragma: no cover
        return
    section = modulecmd.names.modulepath
    data = [modulecmd.module.as_dict(m) for m in modules]
    modulecmd.cache.set(section, path, data)


def factory():  # pragma: no cover
    path = util.split(os.getenv(modulecmd.names.modulepath), os.pathsep)
    return Modulepath(path)


_path = util.singleton(factory)


def path():
    return list(_path.path.keys())


def items():
    for item in _path.path.items():
        yield item


def set_path(other_path):
    global _path
    _path = other_path


def get(key, use_file_modulepath=False):
    return _path.get(key, use_file_modulepath=use_file_modulepath)


def append_path(dirname):
    return _path.append_path(dirname)


def remove_path(dirname):
    return _path.remove_path(dirname)


def prepend_path(dirname):
    return _path.prepend_path(dirname)


def format_avail(**kwargs):
    return _path.format_avail(**kwargs)


def candidates(name):
    return _path.candidates(name)


def contains(path):
    return path in _path


def size():
    return _path.size()


def clear():
    return _path.clear()
