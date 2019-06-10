import pymod.mc
import pymod.modes

category = 'interaction'


def prereq_any(module, mode, *names):
    """Defines prerequisites (modules that must be loaded) for this module

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    names : tuple of str
        Names of prerequisite modules

    Notes
    -----
    In load mode, asserts that at least one of the modules given by `names` is
    loaded.  In unload mode, nothing is done.

    FIXME: This function should execute mc.prereq_any in any mode other than
    unload.  In whatis, help, show, etc. modes, it should register the prereqs
    but not enforce them.

    """
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.load:
        pymod.mc.prereq_any(*names)
