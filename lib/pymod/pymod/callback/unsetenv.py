import pymod.modes
import pymod.environ

category = "environment"


def unsetenv(module, mode, name, *args):
    """Unset value of environment variable `name`

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        name (str): Name of the environment variable

    Notes:
    In unload mode, nothing is done

    Examples:
    Consider the module ``baz``

    .. code-block:: python

        unsetenv("BAZ")

    .. code-block:: console

        $ echo ${BAZ}
        baz

    On loading, the environment variable ``BAZ`` is unset

    .. code-block:: console

        $ module load baz
        $ echo ${BAZ}

    """
    pymod.modes.assert_known_mode(mode)
    if mode != pymod.modes.unload:
        return pymod.environ.unset(name)
