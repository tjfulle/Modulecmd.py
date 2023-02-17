import modulecmd.util

category = "utility"


def set_executable(module, mode, path):
    """Add +x to path

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        path (str): Path to make executable

    """
    return modulecmd.util.set_executable(path)
