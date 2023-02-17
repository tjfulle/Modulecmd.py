import modulecmd.system
import modulecmd.modes
import llnl.util.tty as tty

category = "utility"


def log_warning(module, mode, string, **fmt_kwds):
    """Log a warning message to the user

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        string (str): The warning message

    """
    modulecmd.modes.assert_known_mode(mode)
    tty.warn(string.format(**fmt_kwds), reported_by=module.fullname),
