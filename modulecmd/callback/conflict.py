import modulecmd.system
import modulecmd.modes

category = "interaction"


def conflict(module, mode, *names, **kwargs):
    """Defines conflicts (modules that conflict with `module`)

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        names (tuple of str): Names of conflicting modules

    Notes:
    In load mode, asserts that none of `names` is loaded.   Otherwise, nothing
    is done.

    """
    # FIXME: This function should execute mc.conflict in any mode other than
    # unload.  In whatis, help, show, etc. modes, it should register the
    # conflicts but not enforce them.

    modulecmd.modes.assert_known_mode(mode)
    if mode == modulecmd.modes.load:
        modulecmd.system.conflict(module, *names)
