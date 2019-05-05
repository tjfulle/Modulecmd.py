import os
from .bash import Bash
from .csh import Csh
from .python import Python
from .shell import Shell

from contrib.util.lang import Singleton
import pymod.config


__shells__ = (Shell, Bash, Csh, Python)

default_shell = os.path.basename(os.getenv('SHELL', 'bash'))


def _shell(shell_name=None):
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
        shell_name = pymod.config.get('default_shell')
    for shelltype in __shells__:
        if shell_name == shelltype.name:
            name = shell_name
            return shelltype()
    raise Exception('Unknown shell ' + shell_name)


shell = Singleton(_shell)


def set_shell(shell_name):
    """Set the shell singleton to a specific value. """
    global shell, name
    if shell_name != shell.name:
        shell = _shell(shell_name)


def name():
    return shell.name


def source_command(filename):
    return shell.source_command(filename)


def format_commands(environ=None):
    environ = environ or pymod.environ
    return shell.format_commands(environ)


def dump(environ=None):
    environ = environ or pymod.environ
    shell.dump(environ)


def filter(environ):
    environ = environ or pymod.environ
    return shell.filter(environ)
