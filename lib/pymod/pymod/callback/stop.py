import pymod.error

category = ''


def stop(module, mode):
    """Stop loading this module

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution

    Notes
    -----
    All commands up to the call to `stop` are executed.

    """
    raise pymod.error.StopLoadingModuleError
