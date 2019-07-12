import os
import pymod.mc
import pymod.clone
import pymod.error
from pymod.serialize import deserialize_from_dict

from contrib.util import split


def save(name):
    return pymod.clone.save(name)


def restore(name):
    the_clone = pymod.clone.get(name)
    if the_clone is None:
        raise pymod.error.CloneDoesNotExistError(name)
    restore_impl(the_clone)


def remove(name):
    return pymod.clone.remove(name)


def restore_impl(the_clone):
    # Purge current environment
    pymod.mc.purge(load_after_purge=False)

    mp = the_clone.pop(pymod.names.modulepath, None)
    current_env = pymod.environ.copy(include_os=True)
    for (key, val) in current_env.items():
        if key == pymod.names.modulepath:
            continue
        pymod.environ.unset(key)

    path = pymod.modulepath.Modulepath(split(mp, os.pathsep))
    pymod.modulepath.set_path(path)

    # Make sure environment matches clone
    for (key, val) in the_clone.items():
        pymod.environ.set(key, val)

    # Load modules to make sure aliases/functions are restored
    lm_cellar = deserialize_from_dict(the_clone, pymod.names.loaded_module_cellar)
    if lm_cellar:
        loaded_modules = []
        for ar in lm_cellar:
            try:
                module = pymod.mc.unarchive_module(ar)
            except pymod.error.ModuleNotFoundError:
                raise pymod.error.CloneModuleNotFoundError(ar['fullname'],
                                                           ar['filename'])
            loaded_modules.append(module)
        pymod.mc.set_loaded_modules(loaded_modules)

        for module in loaded_modules:
            pymod.mc.load_partial(module)
