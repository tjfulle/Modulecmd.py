import os
import json

import pymod.module
import pymod.environ
import llnl.util.tty as tty
from llnl.util.lang import Singleton
from llnl.util.filesystem import working_dir
from contrib.util import strip_quotes

"""Functions for finding modules on MODULEPATH"""

marked_default_names = ('default', '.version')


def find_modules(dirname):

    dirname = os.path.expanduser(dirname)
    cached_modules = get_from_cache(dirname)
    if cached_modules is not None:
        return cached_modules

    if dirname == '/':
        raise ValueError('Requesting to find modules in root directory')

    if not os.access(dirname, os.R_OK):  # pragma: no cover
        tty.verbose('Insufficient privileges to read modules in {0!r}'
                    .format(dirname))
        return None

    if not os.path.isdir(dirname):  # pragma: no cover
        tty.verbose('{0!r} is not a directory'.format(dirname))
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

    if not modules:  # pragma: no cover
        tty.verbose('Modulepath: no modules found in {0}'.format(dirname))
        return None

    put_in_cache(dirname, modules)
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


class Cache:
    def __init__(self):
        basename = pymod.names.cache_file_basename
        for dirname in (pymod.paths.user_config_platform_path,
                        pymod.paths.user_config_path):
            filename = os.path.join(dirname, basename)
            if os.path.exists(filename):  # pragma: no cover
                break
        else:
            filename = os.path.join(
                pymod.paths.user_config_platform_path,
                basename)
        self.filename = filename
        self.data = self.load()

    def get(self, modulepath):
        modules_cache = self.data.get(modulepath)
        if not modules_cache:
            return None
        modules = []
        for cached_module in modules_cache:
            module = pymod.module.from_dict(cached_module)
            if module is None:
                # A module was removed, this directory cache should be
                # invalidated so it can be rebuilt
                self.data[modulepath] = None
                return
            modules.append(module)
        return modules

    def load(self):
        data = dict()
        if os.path.isfile(self.filename):
            data.update(dict(json.load(open(self.filename))))
        return data

    def dump(self):
        with open(self.filename, 'w') as fh:
            json.dump(self.data, fh, indent=2)

    def set(self, modulepath, modules):
        self.data[modulepath] = []
        for module in modules:
            self.data[modulepath].append(pymod.module.as_dict(module))
        self.dump()

    def refresh(self):  # pragma: no cover
        for modulepath in self.data:
            self.data[modulepath] = None
            find_modules(modulepath)

    def remove(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)
        self.data = dict()


_cache = Singleton(Cache)


def remove_cache():
    _cache.remove()


def refresh_cache():  # pragma: no cover
    _cache.refresh()


def put_in_cache(modulepath, modules):
    _cache.set(modulepath, modules)


def get_from_cache(modulepath):
    return _cache.get(modulepath)


def reload_cache():
    _cache.data = _cache.load()
