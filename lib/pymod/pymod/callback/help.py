import pymod.modes

category = ''


def help(module, mode, help_string, **kwargs):
    """Sets a help message for `module`

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    help_str : str
        Help message for the module

    """
    pymod.modes.assert_known_mode(mode)
    module.set_help_string(help_string)