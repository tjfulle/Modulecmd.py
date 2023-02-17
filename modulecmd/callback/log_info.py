import modulecmd.xio as xio
import modulecmd.system
import modulecmd.modes

category = "utility"


def log_info(module, mode, string, **fmt_kwds):
    """Log an information message to the user

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        string (str): The informational message

    """
    modulecmd.modes.assert_known_mode(mode)
    message = string.format(**fmt_kwds)
    xio.info(f"{message} [reported by: {module.fullname}]")
