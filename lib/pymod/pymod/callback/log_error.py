import pymod.mc
import pymod.modes
import llnl.util.tty as tty

category = 'utility'


def log_error(module, mode, string):
    """Log an error message to the user to quite

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        string (str): The error message

    """
    pymod.modes.assert_known_mode(mode)
    tty.die(string, reported_by=module.fullname),


log_error.eval_on_show = True