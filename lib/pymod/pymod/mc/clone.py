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
    clones[name] = cloned_env()
    write(clones, filename)
    return clones[name]


def cloned_env():
    return pymod.environ.filtered(include_os=True)


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
    restore_clone_impl(the_clone)


def restore_clone_impl(the_clone):
    # Purge current environment
    pymod.mc.purge(load_after_purge=False)
    dirnames = split(the_clone.pop(pymod.names.modulepath, None), os.pathsep)
    path = pymod.modulepath.Modulepath(dirnames)
    pymod.modulepath.set_path(path)

    # Make sure environment matches clone
    for (key, val) in the_clone.items():
        pymod.environ.set(key, val)

    # Load modules to make sure aliases/functions are restored
    loaded_modules = []
    lm_cellar = the_clone.get(pymod.names.loaded_module_cellar)
    if lm_cellar:
        lm_cellar = str_to_list(lm_cellar)
        for ar in lm_cellar:
            module = pymod.mc.unarchive_module(ar)
            loaded_modules.append(module)
        pymod.mc.set_loaded_modules(loaded_modules)

        for module in loaded_modules:
            pymod.mc.load_partial(module)
