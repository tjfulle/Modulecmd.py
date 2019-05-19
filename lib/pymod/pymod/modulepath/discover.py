import os

import pymod.module
import pymod.environ
import llnl.util.tty as tty
from llnl.util.filesystem import working_dir
from contrib.util import strip_quotes, split

"""Functions for finding modules on MODULEPATH"""

marked_default_names = ('default', '.version')


def find_modules(dirname):
    # Lazy import to avoid circular imports
    import pymod.mc

    dirname = os.path.expanduser(dirname)

    if dirname == '/':
        raise ValueError('Requesting to find modules in root directory')

    if not os.access(dirname, os.R_OK):  # pragma: no cover
        return None

    if not os.path.isdir(dirname):  # pragma: no cover
        return None

    first_level_files, first_level_dirs = listdir(dirname)
    modules = find_modules_n(dirname, first_level_files)

    # find versioned modules
    for name in first_level_dirs:
        # The first level directory is the module's name
        first_level_dir = os.path.join(dirname, name)
        assert os.path.isdir(first_level_dir)
        second_level_files, second_level_dirs = listdir(first_level_dir)
        if second_level_dirs:
            # <dirname>/<name>/<version>/<variants>
            maybe_module_files = [f for f in second_level_files
                                  if f not in marked_default_names]
            if maybe_module_files:  # pragma: no cover
                tty.warn('Skipping files in directory {0} '
                         'with NVV structure'.format(first_level_dir))
            for version in second_level_dirs:
                # The second level directory is the version in NVV format
                modules_nvv = find_modules_nvv(dirname, name, version)
                if modules_nvv:
                    modules.extend(modules_nvv)
        else:
            # <dirname>/<name>/<versions>
            modules_nv = find_modules_nv(dirname, name)
            if modules_nv:
                modules.extend(modules_nv)

    lm_cellar = pymod.mc.get_cellar()
    for module in modules:
        for item in lm_cellar:
            if item.fullname == module.fullname:
                module.opts = item.opts
                break
        else:
            module.opts = None

    return modules


def find_modules_n(dirname, names):
    """Find 'named' modules.  i.e., modules that are not versioned"""
    modules_n = []
    with working_dir(dirname):
        for name in names:
            assert isfilelike(name)
            if name in marked_default_names:  # pragma: no cover
                tty.verbose('Skipping marked default for unversioned '
                            'modules in {0}'.format(dirname))
                continue
            module = pymod.module.module(dirname, name)
            if module is not None:
                modules_n.append(module)
    return modules_n


def find_modules_nv(dirname, name):
    """Find versioned modules. i.e., modules given by
       <dirname>/<name>/<versions...>
    """
    modules_nv = []
    with working_dir(dirname):
        assert os.path.isdir(name)
        versions, dirs = listdir(name)
        if dirs:  # pragma: no cover
            raise ValueError('Expected NV module structure not NVx')
        marked_default = pop_marked_default(name, versions)
        for version in versions:
            module = pymod.module.module(dirname, name, version)
            if module is not None:
                module.marked_as_default = module.filename == marked_default
                modules_nv.append(module)
    return modules_nv


def find_modules_nvv(dirname, name, version):
    """Find VV modules. i.e., modules given by
       <dirname>/<name>/<version>/<variants...>
    """
    modules_nvv = []
    basedir = os.path.join(dirname, name)
    assert os.path.isdir(basedir)
    files, _ = listdir(basedir)
    marked_default = pop_marked_default(basedir, files)
    with working_dir(basedir):
        assert os.path.isdir(version)
        variants, dirs = listdir(version)
        if dirs:  # pragma: no cover
            tty.debug('In {0}, expected NVV module structure not '
                      'NVVx'.format(basedir))
            return None
        for variant in variants:
            module = pymod.module.module(dirname, name, version, variant)
            if module is not None:
                module.marked_as_default = module.filename == marked_default
                modules_nvv.append(module)
    return modules_nvv


def pop_marked_default(dirname, versions):
    dirname = os.path.realpath(dirname)
    assert os.path.isdir(dirname)
    linked_default = pop_linked_default(dirname, versions)
    versioned_default = pop_versioned_default(dirname, versions)
    if linked_default and versioned_default:
        tty.warn('A linked and versioned default exist in {0}, '
                 'choosing the linked'.format(dirname))
        return linked_default
    return linked_default or versioned_default


def pop_linked_default(dirname, files):
    """Look for a file named `default` that is a symlink to a module file"""
    linked_default_name = 'default'
    try:
        files.remove(linked_default_name)
    except ValueError:
        return None

    linked_default_file = os.path.join(dirname, linked_default_name)
    if not os.path.islink(linked_default_file):  # pragma: no cover
        tty.verbose(
            'Modulepath: expected file named `default` in {0} '
            'to be a link to a modulefile'.format(dirname))
        return None

    linked_default_source = os.path.realpath(linked_default_file)
    if not linked_default_source.startswith(dirname):  # pragma: no cover
        tty.warn(
            'Modulepath: expected file named `default` in {0} to be '
            'a link to a modulefile in the same directory'.format(dirname))
        return None

    return linked_default_source


def pop_versioned_default(dirname, files):
    """TCL modules .version scheme"""
    version_file_name = '.version'
    try:
        files.remove(version_file_name)
    except ValueError:
        return None
    version_file = os.path.join(dirname, version_file_name)
    version = read_tcl_default_version(version_file)
    if version is None:  # pragma: no cover
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


def listdir(dirname):
    files, dirs = [], []
    with working_dir(dirname):
        for item in os.listdir('.'):
            if os.path.isdir(item):
                dirs.append(item)
            else:
                files.append(item)
    return files, dirs


def isfilelike(item):
    return os.path.exists(item) and not os.path.isdir(item)
