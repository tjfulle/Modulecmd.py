import pymod.mc
import pymod.modes

category = "utility"


def raw(module, mode, *commands, **kwargs):
    """Runs raw shell commands

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        commands (tuple of str): commands to run

    Keyword arguments:
        when (bool): Logical describing when to run `commands`.  If `None` \
                or `True`, the `commands` are run.

    Notes:
    - **Warning:** This function runs the shell commands unconditionally.  Environment \
            modifications made by the script are not tracked by Modulecmd.py.

    - commands are only run if ``mode()=='load'``

    Examples:
    Consider the module ``baz``:

    .. code-block:: python

        raw("alias bar='spam'", when=mode()=='load')

    The command ``<command>`` will be run when the module is loaded.

    """
    pymod.modes.assert_known_mode(mode)
    when = kwargs.get("when", None)
    if when is not None and not when:
        return
    pymod.mc.raw(*commands)
