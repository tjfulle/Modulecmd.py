import pymod.modes
import pymod.environ

category = ''


def setenv(module, mode, name, value):
    """Set value of environment variable `name`

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    name : str
        Name of the environment variable
    value : str
        Value to set for environment variable `name`

    Notes
    -----
    In load mode, sets the environment variable.  In unload mode, unsets the
    variable.

    """
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.unload:
        return pymod.environ.unset(name)
    else:
        return pymod.environ.set(name, value)