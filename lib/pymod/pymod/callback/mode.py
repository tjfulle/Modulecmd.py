import pymod.modes

category = "utility"


def mode(module, mode):
    """Returns the current mode (load, unload, show, etc)

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution

    Returns:
        modestr (str): The mode of execution

    Examples:
    Consider the module ``baz``

    .. code-block:: python

        # Actions to perform
        ...
        if mode() == 'load':
            # do something

    """
    return pymod.modes.as_string(mode)


mode.eval_on_show = True
