import os
import json
import pymod.mc
import pymod.error
import pymod.names
import pymod.paths
import pymod.environ
from contrib.util import str_to_list, split


def read(filename):
    if os.path.isfile(filename):
        return dict(json.load(open(filename)))
    return dict()


def write(clones, filename):
    with open(filename, 'w') as fh:
        json.dump(clones, fh, indent=2)


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
        else:  # pragma: no cover
            dirname = pymod.paths.user_config_path
        return os.path.join(dirname, basename)


def clone(name):
    """Clone current environment"""
    filename = _clone_file()
    clones = read(filename)
    clones[name] = pymod.environ.filtered()
    write(clones, filename)
    return 0


def remove_clone(name):
    filename = _clone_file()
    clones = read(filename)
    clones.pop(name, None)
    write(clones, filename)


def restore_clone(name):
    filename = _clone_file()
    clones = read(filename)
    if name not in clones:
        raise pymod.error.CloneDoesNotExistError(name)
    the_clone = dict(clones[name])

    # Purge current environment
    pymod.mc.purge(load_after_purge=False)
    dirnames = split(the_clone.pop(pymod.names.modulepath, None), os.pathsep)
    path = pymod.modulepath.Modulepath(dirnames)
    pymod.modulepath.set_path(path)

    # Make sure environment matches clone
    for (key, val) in the_clone.items():
        pymod.environ.set(key, val)

    # Load modules to make sure aliases/functions are restored
    lm_cellar = str_to_list(the_clone[pymod.names.loaded_module_cellar])
    for item in lm_cellar:
        fullname, filename, opts = item[:3]
        module = pymod.modulepath.get(filename)
        if module is None:
            raise pymod.error.ModuleNotFoundError(filename, mp=pymod.modulepath)
        module.opts = opts
        pymod.mc.load_partial(module)
