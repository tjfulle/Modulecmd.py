import pymod.modes
import pymod.environ

category = 'environment'


def unsetenv(module, mode, name):
    """Unset value of environment variable `name`

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    name : str
        Name of the environment variable

    Notes
    -----
    In unload mode, nothing is done

    """
    pymod.modes.assert_known_mode(mode)
    if mode != pymod.modes.unload:
        return pymod.environ.unset(name)
