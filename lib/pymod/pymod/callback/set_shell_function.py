import pymod.modes
import pymod.environ

category = "alias"


def set_shell_function(module, mode, name, value):
    """Define a shell function

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        name (str): Name of the function
        value (str): Value of the function

    Notes:
    In unload mode, undefines the shell function.  Otherwise, defines the shell function

    Examples:
    Consider the module ``baz``

    .. code-block:: python

        set_shell_function('baz', 'ls -l $1')

    On loading ``baz``, the shell function is defined

    .. code-block:: console

        $ module load baz
        $ declare -f baz
        baz ()
        {
            ls -l $1
        }

    On unloading ``baz``, the shell function is undefined

    .. code-block:: console

        $ module ls
        Currently loaded module
            1) baz

        $ module unload baz
        $ declare -f baz

    """
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.unload:
        pymod.environ.unset_shell_function(name)
    else:
        pymod.environ.set_shell_function(name, value)
