import pymod.modes
import pymod.environ

category = 'alias'


def unset_alias(module, mode, name):
    """Undefine a shell alias

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    name : str
        Name of the alias

    Notes
    -----
    In unload mode, nothing is done.  Otherwise, the alias given by `name` is
    undefined.

    """
    pymod.modes.assert_known_mode(mode)
    if mode != pymod.modes.unload:
        pymod.environ.unset_alias(name)
