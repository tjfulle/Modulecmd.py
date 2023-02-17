import os
from .bash import Bash
from .csh import Csh
from .python import Python
from .shell import Shell

import modulecmd.config
from llnl.util.lang import Singleton


__shells__ = (Shell, Bash, Csh, Python)

default_shell = os.path.basename(os.getenv("SHELL", "bash"))


def get_shell(shell_name=None):
    """Shell factory method

    Parameters
    ----------
    shell_name : str
        The name of the shell

    Returns
    -------
    shell : Shell
        The instantiated shell whose type's name matches shell_name

    """
    global name
    if shell_name is None:
        shell_name = modulecmd.config.get("default_shell")
    for shelltype in __shells__:
        if shell_name == shelltype.name:
            name = shell_name
            return shelltype()
    raise ValueError("Unknown shell " + shell_name)


_shell = Singleton(get_shell)
name = None


def set_shell(shell_name):
    """Set the shell singleton to a specific value. """
    global _shell, name
    if shell_name != _shell.name:
        _shell = get_shell(shell_name)


def format_source_command(filename, *args):
    return _shell.format_source_command(filename, *args)


def format_output(
    environ,
    aliases=None,
    shell_functions=None,
    files_to_source=None,
    raw_shell_commands=None
):
    return _shell.format_output(
        environ,
        aliases=aliases,
        shell_functions=shell_functions,
        files_to_source=files_to_source,
        raw_shell_commands=raw_shell_commands
    )


def filter_env(environ):
    return _shell.filter_env(environ)


def filter_key(key):
    return _shell.filter_key(key)


def switch():  # pragma: no cover
    return _shell.switch()
