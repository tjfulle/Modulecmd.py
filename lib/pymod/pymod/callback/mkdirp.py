import llnl.util.filesystem

category = 'utility'


def mkdirp(module, mode, *paths, **kwargs):
    """Make directory and all intermediate directories, if necessary.

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        paths (tuple of str): Paths to create

    Keyword arguments:
        mode (permission bits): optional permissions to set on the created directory \
                -- uses OS default if not provided

    Notes:
    This is a wrapper to `llnl.util.filesystem.mkdirp`.

    """
    return llnl.util.filesystem.mkdirp(*paths, **kwargs)
