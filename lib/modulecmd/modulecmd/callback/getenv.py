import modulecmd.system
import modulecmd.modes
import modulecmd.environ

category = "utility"


def getenv(module, mode, key, default=None):
    """Return the value of the environment variable `key` if it exists, or `default` if it doesn't.

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        key (str): The environment variable

    Keyword Arguments:
        default (str): The default value

    Returns:
        value (str): The value of the environment variable `key` if it exists, or `default` if it doesn't.

    Notes:
    - Retrieves values of environment variables from current active
      environment. The difference between `getenv` and `os.getenv` is that
      `os.getenv` is not updated to reflect environment variables that may be
      have set in this, or other modules, load/unloaded in this session.

    """
    modulecmd.modes.assert_known_mode(mode)
    return modulecmd.environ.get(key, default=default)


getenv.eval_on_show = True
