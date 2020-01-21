import pymod.error

category = "utility"


def stop(module, mode):
    """Stop loading this module at this point

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution

    Notes:
    All commands up to the call to `stop` are executed.

    Examples:
    Consider the module ``baz``

    .. code-block:: python

        # Actions to perform
        ...
        if condition:
            stop()

        # Actions not performed if condition is met

    """
    raise pymod.error.StopLoadingModuleError


stop.eval_on_show = True
