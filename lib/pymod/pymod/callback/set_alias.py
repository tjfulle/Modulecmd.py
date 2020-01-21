import pymod.modes
import pymod.environ

category = "alias"


def set_alias(module, mode, name, value):
    """Define a shell alias

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        name (str): Name of the alias
        value (str): Value of the alias

    Notes:
    In unload mode, undefines the alias.  Otherwise, defines the alias.

    Examples:
    Consider the module ``baz``

    .. code-block:: python

        set_alias('baz', 'ls -l')

    On loading ``baz``, the alias is defined

    .. code-block:: console

        $ module load baz
        $ alias baz
        alias baz='ls -l'

    On unloading ``baz``, the alias is undefined

    .. code-block:: console

        $ module ls
        Currently loaded module
            1) baz

        $ module unload baz
        $ alias baz
        -bash: alias: baz: not found

    """
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.unload:
        pymod.environ.unset_alias(name)
    else:
        pymod.environ.set_alias(name, value)
