import pymod.modes

category = 'info'


def help(module, mode, help_string, **kwargs):
    """Sets a help message for `module`

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        help_string (str): Help message for the module

    Notes:
    This function sets the help string displayed by

    .. code-block:: console

        $ module help <name>

    """
    pymod.modes.assert_known_mode(mode)
    module.set_help_string(help_string)
