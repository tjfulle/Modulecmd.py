import os
import subprocess
import modulecmd.modes
import modulecmd.environ
import llnl.util.tty as tty
from modulecmd.util.lang import split
from spack.util.executable import Executable

category = "utility"


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
    modulecmd.modes.assert_known_mode(mode)
    if when is not None and not when:
        return

    xc = split(command, " ", 1)
    exe = Executable(xc[0])
    with open(os.devnull, "a") as fh:
        kwargs = {
            "env": modulecmd.environ.filtered(),
            "output": fh,
            "error": subprocess.sys.stdout,
        }
        try:
            exe(*xc[1:], **kwargs)
        except:  # noqa: E722;  pragma: no cover
            tty.warn("Command {0!r} failed".format(command))
    return
