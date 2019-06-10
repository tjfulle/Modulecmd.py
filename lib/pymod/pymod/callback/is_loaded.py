import pymod.modes
import pymod.modulepath

category = ''


def is_loaded(module, mode, name):
    """Report whether the module `name` is loaded

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    name : str
        Name of the module to report

    Returns
    -------
    bool
        Whether the module given by `name` is loaded

    """
    pymod.modes.assert_known_mode(mode)
    other = pymod.modulepath.get(name)
    if other is None:
        return None
    return other.is_loaded