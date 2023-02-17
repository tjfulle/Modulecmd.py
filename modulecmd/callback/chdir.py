import modulecmd.modes
import modulecmd.environ


category = "utility"


def chdir(module, mode, dirname):
    """Change directory to `dirname` after module is loaded

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        dirname (str): The name of the directory

    """
    if mode == modulecmd.modes.load:
        modulecmd.environ.set_destination_dir(dirname)
