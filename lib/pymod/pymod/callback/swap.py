import pymod.mc
import pymod.modes

category = 'module'


def swap(module, mode, cur, new, **kwargs):
    """Swap module `cur` for module `new`

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    cur : str
        The name of the module to unload
    new : str
        The name of the module to load in place of `cur`

    Returns
    -------
    Module
       `cur`'s module object

    Notes
    -----
    In load mode, perform an unload of `cur` followed by a load of `new`.
    However, when unloading `cur`, all modules loaded after `cur` are also
    unloaded in reverse order.  After loading `new`, the unloaded modules are
    reloaded in the order they were originally loaded.  If MODULEPATH
    changes as a result of the swap, it is possible that some of these modules
    will be swapped themselves, or not reloaded at all.

    In unload mode, the swap is not performed.

    """
    pymod.modes.assert_known_mode(mode)
    if mode != pymod.modes.unload:
        # We don't swap modules in unload mode
        return pymod.mc.swap(cur, new, caller='modulefile')
