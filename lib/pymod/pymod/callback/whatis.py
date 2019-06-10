import pymod.modes

category = ''


def whatis(module, mode, *args, **kwargs):
    """Sets the "whatis" informational string for `module`

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    args : tuple of str
        Information about the module

    """
    pymod.modes.assert_known_mode(mode)
    return module.set_whatis(*args, **kwargs)