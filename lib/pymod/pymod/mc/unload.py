import pymod.mc
import pymod.modes
import pymod.modulepath
import llnl.util.tty as tty
from pymod.error import ModuleNotFoundError, ModuleNotLoadedError


def unload(name, tolerant=False, caller='command_line'):
    """Unload the module given by `name`"""
    module = pymod.modulepath.get(name)
    if module is None:
        raise ModuleNotFoundError(name)

    loaded_modules = pymod.mc.get_loaded_modules()
    for loaded in loaded_modules:
        if loaded.name == name:
            break
        elif loaded.fullname == name:
            break
    else:
        tty.warn('Module {0} is not loaded'.format(name))
        return
    unload_impl(loaded, caller)
    return loaded


def unload_impl(module, caller='command_line'):
    """Implementation of unload

    Parameters
    ----------
    module : Module
        The module to unload
    """
    if not module.is_loaded:
        if caller == 'command_line':
            raise ModuleNotLoadedError(module)
        return

    if module.refcount == 1 or caller == 'command_line':
        pymod.mc.execmodule(module, pymod.modes.unload)
        pymod.mc.unregister_module(module)
    else:
        pymod.mc.decrement_refcount(module)

    module.reset_state()
