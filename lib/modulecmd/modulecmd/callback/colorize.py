import llnl.util.tty.color

category = "utility"


def colorize(module, mode, string, **kwargs):
    """Replace all color expressions in a string with ANSI control codes.

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        string (str): The string to replace

    Keyword arguments:
        color (bool): If False, output will be plain text without control \
            codes, for output to non-console devices.

    Returns:
        colorized (str): The filtered string

    Notes:
    This is a wrapper to `llnl.util.tty.color.colorize`.

    """
    return llnl.util.tty.color.colorize(string, **kwargs)
