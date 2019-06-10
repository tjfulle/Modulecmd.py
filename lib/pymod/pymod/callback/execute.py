import pymod.mc
import pymod.modes

category = 'utility'


def execute(module, mode, command, when=None):
    """Executes the command `command` in a subprocess

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    command : str
        The command to execute in a shell subprocess
    when : bool
        Logical describing when to execute `command`.  If `None` or `True`,
        `command` is executed.

    """
    pymod.modes.assert_known_mode(mode)
    if when is not None and not when:
        return
    pymod.mc.execute(command)
