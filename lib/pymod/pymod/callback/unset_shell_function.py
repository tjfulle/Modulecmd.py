import pymod.modes
import pymod.environ

category = ''


def unset_shell_function(module, mode, name):
    """Undefine a shell function

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    name : str
        Name of the function

    Notes
    -----
    In unload mode, nothing is done.  Otherwise, the function given by `name` is
    undefined.

    """
    pymod.modes.assert_known_mode(mode)
    if mode != pymod.modes.unload:
        pymod.environ.unset_shell_function(name)