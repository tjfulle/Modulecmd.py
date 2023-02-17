import socket
import modulecmd.modes

category = "utility"


def get_hostname(module, mode):
    """Returns the hostname

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution

    Returns:
        hostname (str): string containing the hostname of the machine where the Python interpreter is currently executing

    """
    modulecmd.modes.assert_known_mode(mode)
    return socket.gethostname()


get_hostname.eval_on_show = True
