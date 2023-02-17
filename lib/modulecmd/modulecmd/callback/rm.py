import os
import shutil
import llnl.util.filesystem

category = "utility"


def rm(module, mode, *paths):
    """Remove file or directory

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        paths (tuple of str): Paths to create

    Notes:
    This is a wrapper to `llnl.util.filesystem.mkdirp`.

    """
    for path in paths:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            llnl.util.filesystem.force_remove(path)
