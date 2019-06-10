import llnl.util.filesystem

category = 'utility'


def mkdirp(module, mode, *paths, **kwargs):
    """Make directory `dir` and all intermediate directories, if necessary.

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    paths : tuple of str
        Paths to create

    kwargs : dict
        mode (permission bits or None, optional): optional permissions to
            set on the created directory -- use OS default if not provided

    Notes
    -----
    This is a wrapper to `llnl.util.filesystem.mkdirp`.

    """
    return llnl.util.filesystem.mkdirp(*paths, **kwargs)
