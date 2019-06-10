import contrib.util

category = 'utility'


def listdir(module, mode, dirname, key=None):
    """List contents of directory `dirname`

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    dirname : str
        Path to directory
    key : callable
        Filter for contents in `dirname`

    Returns
    -------
    list
        Contents of `dirname`

    """
    return contrib.util.listdir(dirname, key=key)
