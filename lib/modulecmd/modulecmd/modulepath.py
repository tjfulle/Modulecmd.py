import os
import re
import bisect
from io import StringIO
from string import Template
from collections import OrderedDict as ordered_dict


import modulecmd.alias
import modulecmd.names
import modulecmd.module
from modulecmd.util import join, split, groupby, working_dir, singleton, terminal_size

import llnl.util.tty as tty
from llnl.util.tty.color import colorize
from llnl.util.tty.colify import colified


def expand_name(dirname):
    return os.path.expanduser(Template(dirname).safe_substitute(**(os.environ)))


class Modulepath:
    def __init__(self, directories):
        self.path = ordered_dict()
        for directory in directories:
            path = expand_name(directory)
            modules = find_modules(path)
            if not modules:
                continue
            self.path[path] = modules
        self.defaults = {}
        self.assign_defaults()

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
        for (path, modules) in self.path.items():
            if path == dirname:
                return modules

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
        dirname = expand_name(dirname)
        if dirname in self:
            return
        modules = find_modules(dirname)
        if not modules:
            tty.verbose(f"No modules found in {dirname}")
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
        width = terminal_size().columns
        # head = lambda x: (" " + x + " ").center(width, "-")
        for (directory, modules) in self.path.items():
            modules = sorted([m for m in modules if m.is_enabled], key=self.sort_key)
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
        for (directory, modules) in self.path.items():
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
        for modules in self.path.values():
            if not modules:  # pragma: no cover
                continue
            for module in modules:
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


marked_default_names = ("default", ".version")
skip_dirs = (".git", ".svn", "CVS")


def find_modules2(root, branch=None):
    modules = []
    if root == "/":
        tty.verbose("Requesting to find modules in root directory")
        return []
    elif root in (".git", ".svn", "CVS"):  # pragma: no cover
        return []
    with working_dir(root):
        for p in os.listdir(branch or "."):
            if modulecmd.module.ishidden(p):
                continue
            f = os.path.normpath(os.path.join(branch or ".", p))
            if modulecmd.module.ismodule(f):
                m = modulecmd.factory(root, f)
                if m.enabled:
                    modules.append(m)
            elif os.path.isdir(f):
                modules.extend(find_modules2(root, branch=f))
    return sorted(modules, key=modulesorter)


def find_modules(directory):
    cached_modules = get_cached_modules(directory)
    if cached_modules is not None:
        return cached_modules
    else:
        modules = _find_modules(directory)
        if modules:
            cache_modules(directory, modules)
        return modules


def _find_modules(directory):

    directory = os.path.expanduser(directory)

    if directory == "/":
        tty.verbose("Requesting to find modules in root directory")
        return None

    if not os.access(directory, os.R_OK):
        tty.verbose("{0!r} is not an accessible directory".format(directory))
        return None

    if not os.path.isdir(directory):  # pragma: no cover
        # This should be redundant because of the previous check
        tty.verbose("{0!r} is not a directory".format(directory))
        return None

    return _find(directory)


def _find(directory):

    defaults = {}
    dir_modules = {}
    directory = os.path.abspath(directory)

    for (dirname, dirs, files) in os.walk(directory):

        if os.path.basename(dirname) in skip_dirs:
            del dirs[:]
            continue

        explicit_default = pop_marked_default(dirname, files)
        if explicit_default is not None:
            key = dirname.replace(directory + os.path.sep, "")
            defaults[key] = explicit_default

        modulefiles = []
        for basename in files:
            if basename.startswith("."):
                continue
            f = os.path.join(dirname, basename)
            path = f.replace(directory + os.path.sep, "")
            module = modulecmd.module.factory(directory, path)
            if module is None:
                continue
            modulefiles.append(module)

        if not modulefiles:
            continue

        for module in modulefiles:
            dir_modules.setdefault(module.name, []).append(module)

    mark_explicit_defaults(dir_modules, defaults)
    modules = [m for (_, modules) in dir_modules.items() for m in modules] or None
    return modules


def mark_explicit_defaults(modules, defaults):
    for (name, filename) in defaults.items():
        mods = modules.get(name)
        if mods is None:
            tty.debug("There is no module named {0}".format(name))
            continue
        for module in mods:
            if os.path.realpath(module.filename) == os.path.realpath(filename):
                module.marked_as_default = True
                break
        else:
            tty.verbose("No matching module to mark default for {0}".format(name))


def pop_marked_default(dirname, versions):
    dirname = os.path.realpath(dirname)
    assert os.path.isdir(dirname)
    linked_default = pop_linked_default(dirname, versions)
    versioned_default = pop_versioned_default(dirname, versions)
    if linked_default and versioned_default:
        tty.verbose(
            "A linked and versioned default exist in {0}, "
            "choosing the linked".format(dirname)
        )
        return linked_default
    return linked_default or versioned_default


def pop_linked_default(dirname, files):
    """Look for a file named `default` that is a symlink to a module file"""
    linked_default_name = "default"
    try:
        files.remove(linked_default_name)
    except ValueError:
        return None

    linked_default_file = os.path.join(dirname, linked_default_name)
    if not os.path.islink(linked_default_file):
        tty.verbose(
            "Modulepath: expected file named `default` in {0} "
            "to be a link to a modulefile".format(dirname)
        )
        return None

    linked_default_source = os.path.realpath(linked_default_file)
    if not os.path.dirname(linked_default_source) == dirname:
        tty.verbose(
            "Modulepath: expected file named `default` in {0} to be "
            "a link to a modulefile in the same directory".format(dirname)
        )
        return None

    return linked_default_source


def pop_versioned_default(dirname, files):
    """TCL modules .version scheme"""
    version_file_name = ".version"
    try:
        files.remove(version_file_name)
    except ValueError:
        return None
    version_file = os.path.join(dirname, version_file_name)
    version = read_tcl_default_version(version_file)
    if version is None:
        tty.verbose("Could not determine .version default in {0}".format(dirname))
    else:
        default_file = os.path.join(dirname, version)
        if os.path.exists(default_file):
            return default_file
        tty.verbose("{0!r}: version default does not exist".format(default_file))


def read_tcl_default_version(filename):
    with open(filename) as fh:
        for (i, line) in enumerate(fh.readlines()):
            line = " ".join(line.split())
            if i == 0 and not line.startswith("#%Module"):
                tty.debug("version file does not have #%Module header")
            if line.startswith("set ModulesVersion"):
                raw_version = line.split("#", 1)[0].split()[-1]
                try:
                    version = eval(raw_version)
                except (SyntaxError, NameError):
                    version = raw_version
                return version
    return None


def listdir(dirname):
    files, dirs = [], []
    if not os.access(dirname, os.X_OK):  # pragma: no cover
        return [], []
    with working_dir(dirname):
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
    path = split(os.getenv(modulecmd.names.modulepath), os.pathsep)
    return Modulepath(path)


_path = singleton(factory)


def path():
    return list(_path.path.keys())


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


def avail(**kwargs):
    return _path.avail(**kwargs)


def candidates(name):
    return _path.candidates(name)


def contains(path):
    return path in _path


def size():
    return _path.size()


def clear():
    return _path.clear()
