import llnl.util.filesystem

category = "utility"


def set_executable(module, mode, path):
    """Add +x to path

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        path (str): Path to make executable

    Notes:
    This is a wrapper to `llnl.util.filesystem.set_executable`.

    """
    return llnl.util.filesystem.set_executable(path)
