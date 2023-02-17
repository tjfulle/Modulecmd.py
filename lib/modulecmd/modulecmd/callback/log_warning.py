import modulecmd.xio as xio
import modulecmd.system
import modulecmd.modes

category = "utility"


def log_warning(module, mode, string, **fmt_kwds):
    """Log a warning message to the user

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        string (str): The warning message

    """
    modulecmd.modes.assert_known_mode(mode)
    message = string.format(**fmt_kwds)
    xio.warn(f"{message} [reported by: {module.fullname}]")
