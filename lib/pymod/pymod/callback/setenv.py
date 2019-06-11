import pymod.modes
import pymod.environ

category = 'environment'


def setenv(module, mode, name, value):
    """Set value of environment variable `name`

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        name (str): Name of the environment variable
        value (str): Value to set for environment variable `name`

    Notes:
    In unload mode, the environment variable is unset.  Otherwise, it is set.

    Examples:
    Consider the module ``baz``

    .. code-block:: python

        setenv('BAZ', 'baz')

    On loading ``baz``, the environment variable is set

    .. code-block:: console

        $ module load baz
        $ echo ${BAZ}
        baz

    On unloading ``baz``, the environment variable is unset

    .. code-block:: console

        $ module ls
        Currently loaded module
            1) baz

        $ module unload baz
        $ echo ${BAZ}

    """
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.unload:
        return pymod.environ.unset(name)
    else:
        return pymod.environ.set(name, value)
