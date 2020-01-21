import pymod.mc
import pymod.modes
import llnl.util.tty as tty

category = "utility"


def log_info(module, mode, string):
    """Log an information message to the user

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        string (str): The informational message

    """
    pymod.modes.assert_known_mode(mode)
    tty.info(string, reported_by=module.fullname),
