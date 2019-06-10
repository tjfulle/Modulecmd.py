import pymod.mc
import pymod.modes

category = ''


def unuse(module, mode, dirname):
    """Remove the directory `dirname` from MODULEPATH

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    dirname : str
        Name of the directory to remove from MODULEPATH

    Notes
    -----
    In load mode, removes `dirname` from MODULEPATH (it it is on MODULEPATH).
    In unload mode, nothing is done.

    This function potentially has side effects on the environment.  When
    a directory is `unuse`d, modules in its path will become unavailable and, if
    loaded, will be unloaded.

    """
    pymod.modes.assert_known_mode(mode)
    if mode != pymod.modes.unload:
        pymod.mc.unuse(dirname)