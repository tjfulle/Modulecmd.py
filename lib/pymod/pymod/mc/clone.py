import os
import json
import pymod.mc
import pymod.error
import pymod.names
import pymod.paths
import pymod.environ
from contrib.util import str2dict


def read(filename):
    if os.path.isfile(filename):
        return dict(json.load(open(filename)))
    return dict()


def _clone_file():
    basename = pymod.names.clones_file_basename
    for dirname in (pymod.paths.user_config_platform_path,
                    pymod.paths.user_config_path):
        filename = os.path.join(dirname, basename)
        if os.path.exists(filename):
            return filename
    else:
        if os.path.exists(pymod.paths.user_config_platform_path):
            dirname = pymod.paths.user_config_platform_path
        else:
            dirname = pymod.paths.user_config_path
        return os.path.join(dirname, basename)


def clone(name):
    """Clone current environment"""
    filename = _clone_file()
    clones = read(filename)
    clones[name] = pymod.environ.filtered()
    with open(filename, 'w') as fh:
        json.dump(clones, fh, indent=2)
    return 0


def restore_clone(name):
    filename = _clone_file()
    clones = read(filename)
    if name not in clones:
        raise CloneDoesNotExistError(name)
    the_clone = dict(clones[name])

    # Purge current environment
    pymod.mc.purge(load_after_purge=False)
    dirnames = the_clone[pymod.names.modulepath].split(os.pathsep)
    path = pymod.modulepath.Modulepath(dirnames)
    pymod.modulepath.set_path(path)

    # Make sure environment matches clone
    for (key, val) in the_clone.items():
        pymod.environ.set(key, val)

    # Load modules to make sure aliases/functions are restored
    module_files = the_clone[pymod.names.loaded_module_files].split(os.pathsep)
    module_opts = str2dict(the_clone[pymod.names.loaded_module_opts])

    for (i, filename) in enumerate(module_files):
        module = pymod.modulepath.get(filename)
        if module is None:
            raise pymod.error.ModuleNotFoundError(filename, mp=pymod.modulepath)
        module.opts = module_opts.get(module.fullname)
        pymod.mc.load_partial(module)


class CloneDoesNotExistError(Exception):
    def __init__(self, name):
        msg = '{0!r} is not a cloned environment'.format(name)
        super(CloneDoesNotExistError, self).__init__(msg)
