import pymod.mc
import pymod.modes
from pymod.error import ModuleNotFoundError

category = 'module'


def unload(module, mode, name):
    """Unload the module `name`

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    name : str
        Name of the module to unload

    Returns
    -------
    Module
        The loaded module

    Notes
    -----
    In load mode, decrements the reference count of the module found by `name`.
    If the reference count drops to 0, the module is unloaded.

    If the module is not found, or is not loaded, nothing is done.

    In unload mode, nothing is done.

    """
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.unload:
        # We are in unload mode and the module was requested to be
        # unloaded. But, we don't know if it was previously loaded. So we
        # skip
        return
    else:
        try:
            pymod.mc.unload(name, caller='modulefile')
        except ModuleNotFoundError:
            return None
