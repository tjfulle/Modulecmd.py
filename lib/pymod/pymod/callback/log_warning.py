import pymod.mc
import pymod.modes
import llnl.util.tty as tty

category = 'utility'


def log_warning(module, mode, string):
    """Log a warning message to the user

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        string (str): The warning message

    """
    pymod.modes.assert_known_mode(mode)
    tty.warn(string, reported_by=module.fullname),