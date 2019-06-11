import pymod.mc
import pymod.modes

category = 'utility'


def execute(module, mode, command, when=None):
    """Executes the command `command` in a subprocess

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        command (str): The command to execute in a shell subprocess

    Keyword arguments:
        when (bool): Logical describing when to execute `command`.  If `None` \
                or `True`, `command` is executed.

    Examples:
    Consider the module ``baz``:

    .. code-block:: python

        execute(<command>, when=mode()=='load')

    The command ``<command>`` will be executed in a subprocess when the module is loaded.

    """
    pymod.modes.assert_known_mode(mode)
    if when is not None and not when:
        return
    pymod.mc.execute(command)
