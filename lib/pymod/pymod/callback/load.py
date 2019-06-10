import pymod.mc
import pymod.modes
from pymod.error import ModuleNotFoundError

category = ''


def load(module, mode, name, **kwds):
    """Load the module `name`

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    name : str
        Name of the module to load

    Returns
    -------
    Module
        The loaded module

    Raises
    ------
    ModuleNotFoundError
        If no available module is found by `name`

    Notes
    -----
    In load mode, loads the module found by `name` if it is not already loaded.
    If it is loaded, its internal reference count is incremented.

    In unload mode, decrements the reference count of the module found by
    `name`.  If the reference count gets to 0, the module is unloaded.

    """
    pymod.modes.assert_known_mode(mode)
    opts = kwds.get('opts', None)
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.unload:
        # We are in unload mode and the module was requested to be loaded.
        # So, we reverse the action and unload it
        try:
            pymod.mc.unload(name, caller='modulefile')
        except ModuleNotFoundError:
            return
    else:
        pymod.mc.load(name, opts=opts, caller='modulefile')