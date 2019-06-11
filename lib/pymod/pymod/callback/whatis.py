import pymod.modes

category = 'info'


def whatis(module, mode, *args, **kwargs):
    """Sets the "whatis" informational string for `module`

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        args (tuple of str): Information about the module

    Notes:
    - This function sets the information string displayed by

    .. code-block:: console

        $ module whatis <name>

    - Keyword arguments are interpreted as ``{title: description}``

    Examples:
    Consider the module ``baz``:

    .. code-block:: python

        whatis("A description about the module",
               a_title="A section in the whatis")

    .. code-block:: console

        $ module whatis baz
        A description about the module

        A Title
        A section in the whatis

    """
    pymod.modes.assert_known_mode(mode)
    return module.set_whatis(*args, **kwargs)
