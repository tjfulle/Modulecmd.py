import pymod.mc
import pymod.modes

category = 'interaction'


def prereq(module, mode, *names):
    """Defines a prerequisite (module that must be loaded) for this module

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    name : str
        Name of the prerequisite module

    Notes
    -----
    In load mode, asserts that `name` is loaded.  Otherwise, nothing is done.

    FIXME: This function should execute mc.prereq in any mode other than
    unload.  In whatis, help, show, etc. modes, it should register the prereqs
    but not enforce them.

    """
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.load:
        pymod.mc.prereq(*names)
