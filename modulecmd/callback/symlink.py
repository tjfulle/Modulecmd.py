import modulecmd.util

category = "utility"


def symlink(module, mode, src, dst):
    """Create a symbolic link from src to dst

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        src (str): Source path
        dst (str): Destination path

    """
    return modulecmd.util.force_symlink(src, dst)
