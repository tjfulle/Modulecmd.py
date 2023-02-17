from modulecmd.util.lang import listdir as _listdir

category = "utility"


def listdir(module, mode, dirname, key=None):
    """List contents of directory `dirname`

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        dirname (str): Path to directory

    Keyword arguments:
        key (callable): Filter for contents in `dirname`

    Returns:
        contents (list): Contents of `dirname`

    Notes:
    - This is a wrapper to ``modulecmd.util.listdir``
    - If ``key`` is given, it must be a callable object

    """
    return _listdir(dirname, key=key)
