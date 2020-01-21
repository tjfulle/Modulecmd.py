import pymod.modes
import pymod.environ

category = "alias"


def unset_alias(module, mode, name):
    """Undefine a shell alias

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        name (str): Name of the shell alias

    Notes:
    In unload mode, nothing is done.  Otherwise, the alias given by `name` is undefined

    Examples:
    Consider the module ``baz``

    .. code-block:: python

        unset_alias("baz")

    .. code-block:: console

        $ alias baz
        alias baz='echo "I am a baz!"'

    On loading, the alias ``baz`` is undefined

    .. code-block:: console

        $ module load baz
        $ alias baz
        -bash: alias: baz: not found

    """
    pymod.modes.assert_known_mode(mode)
    if mode != pymod.modes.unload:
        pymod.environ.unset_alias(name)
