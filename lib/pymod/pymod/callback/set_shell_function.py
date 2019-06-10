import pymod.modes
import pymod.environ

category = 'alias'


def set_shell_function(module, mode, name, value):
    """Define a shell function

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    name : str
        Name of the function
    value : str
        Value of the function

    Notes
    -----
    In load mode, defines the shell function.  In unload mode, undefines it.

    """
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.unload:
        pymod.environ.unset_shell_function(name)
    else:
        pymod.environ.set_shell_function(name, value)
