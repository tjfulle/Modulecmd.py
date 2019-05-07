import os

import pymod.module
import pymod.environ
import llnl.util.tty as tty
from contrib.util import strip_quotes

"""Functions for finding modules on MODULEPATH"""


def find_modules(directory):

    if not os.access(directory, os.R_OK):
        return None

    if directory == '/':
        raise ValueError('Searching root file system!')

    if not os.path.isdir(directory):
        return None

    modules = []
    for (dirname, _, files) in os.walk(directory):
        modules_in_dir = _find_modules(directory, dirname, files)
        modules.extend(modules_in_dir)

    module_opts = pymod.environ.get_dict(pymod.names.loaded_module_opts)
    for module in modules:
        module.opts = module_opts.get(module.fullname)

    return modules


def _find_modules(rootdir, dirname, files):

    modules_this_dir = []
    if not files:
        return modules_this_dir

    # Determine if there is an explicit default
    linked_default = _linked_default_file(dirname, files)
    versioned_default = _versioned_default_file(dirname, files)
    if linked_default and versioned_default:
        tty.warn('A linked and versioned default exist for {0}, '
                     'choosing the linked'.format(os.path.basename(dirname)))
        explicit_default = linked_default
    else:
        explicit_default = linked_default or versioned_default

    # Look for modules
    for filename in files:
        filepath = os.path.join(dirname, filename)
        module = pymod.module.from_file(rootdir, filepath)
        if module is not None:
            module.is_explicit_default = module.filename == explicit_default
            modules_this_dir.append(module)
    return sorted(modules_this_dir, key=lambda module: module.fullname)


def _linked_default_file(dirname, files):
    """Look for a file named `default` that is a symlink to a module file"""
    linked_default_name = 'default'
    try:
        files.remove(linked_default_name)
    except ValueError:
        return None

    linked_default_file = os.path.join(dirname, linked_default_name)
    if not os.path.islink(linked_default_file):
        tty.verbose(
            'Modulepath: expected file named `default` in {0} '
            'to be a link to a modulefile'.format(dirname))
        return None

    linked_default_source = os.path.realpath(linked_default_file)
    if os.path.dirname(linked_default_source) != dirname:
        tty.warn(
            'Modulepath: expected file named `default` in {0} to be '
            'a link to a modulefile in the same directory'.format(dirname))
        return None

    return linked_default_source


def _versioned_default_file(dirname, files):
    """TCL modules .version scheme"""
    version_file_name = '.version'
    try:
        files.remove(version_file_name)
    except ValueError:
        return None
    version_file = os.path.join(dirname, version_file_name)
    version = read_tcl_default_version(version_file)
    if version is None:
        tty.warn(
            'Could not determine .version default in {0}'.format(dirname))
    else:
        default_file = os.path.join(dirname, version)
        if os.path.exists(default_file):
            return default_file
        tty.warn(
            '{0!r}: version default does not exist'.format(default_file))


def read_tcl_default_version(version_file):
    regex = """(?i)^\s*set\s+ModulesVersion"""
    for line in open(version_file).readlines():
        if " ".join(line.split()).startswith('set ModulesVersion'):
            tmp = line.split("#", 1)[0].split()[-1]
            version = strip_quotes(tmp)
            return version
