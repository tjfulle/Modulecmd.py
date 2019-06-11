import contrib.util

category = 'utility'


def check_output(module, mode, command):
    """Run command with arguments and return its output as a string.

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        command (str): The command to run

    Returns:
        output (str): The output of `command`

    Notes:
    This is a wrapper to `contrib.util.check_output`.  Where
    `subprocess.check_output` exists, it is called.  Otherwise, an implementation of
    `subprocess.check_output` is provided.

    """
    return contrib.util.check_output(command)
