import modulecmd.xio as xio
import modulecmd.system
import modulecmd.modes

category = "utility"


def log_error(module, mode, string, **fmt_kwds):
    """Log an error message to the user to quite

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        string (str): The error message

    """
    modulecmd.modes.assert_known_mode(mode)
    message = string.format(**fmt_kwds)
    xio.die(f"{message} [reported by: {module.fullname}]")


log_error.eval_on_show = True
