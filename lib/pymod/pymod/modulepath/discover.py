import os

import pymod.module
import pymod.environ

import llnl.util.tty as tty
from llnl.util.filesystem import working_dir

"""Functions for finding modules on MODULEPATH"""

marked_default_names = ("default", ".version")
skip_dirs = (".git", ".svn", "CVS")


def find_modules(directory):

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
            module = pymod.module.factory(directory, path)
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
