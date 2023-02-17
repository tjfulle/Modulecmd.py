import modulecmd.modes
import modulecmd.environ

category = "alias"


def unset_shell_function(module, mode, name):
    """Undefine a shell function

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        name (str): Name of the shell function

    Notes:
    In unload mode, nothing is done.  Otherwise, the function given by `name` is undefined

    Examples:
    Consider the module ``baz``

    .. code-block:: python

        unset_shell_function("baz")

    .. code-block:: console

        $ declare -f baz
        baz ()
        {
            echo "I am a baz!"
        }

    On loading, the shell function ``baz`` is undefined

    .. code-block:: console

        $ module load baz
        $ declare -f baz

    """
    modulecmd.modes.assert_known_mode(mode)
    if mode != modulecmd.modes.unload:
        modulecmd.environ.unset_shell_function(name)
