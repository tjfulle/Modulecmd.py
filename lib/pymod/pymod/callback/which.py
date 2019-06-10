import contrib.util

category = 'utility'


def which(module, mode, exename):
    """Return the path to an executable, if found on PATH

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    exename : str
        The name of the executable

    Returns
    -------
    str
        The full path to the executable

    Notes
    -----
    This is a wrapper to `contib.util.which`.

    """
    return contrib.util.which(exename)
