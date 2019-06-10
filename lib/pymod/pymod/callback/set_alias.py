import pymod.modes
import pymod.environ

category = 'alias'


def set_alias(module, mode, name, value):
    """Define a shell alias

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    name : str
        Name of the alias
    value : str
        Value of the alias

    Notes
    -----
    In load mode, defines the shell alias.  In unload mode, undefines it.

    """
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.unload:
        pymod.environ.unset_alias(name)
    else:
        pymod.environ.set_alias(name, value)
