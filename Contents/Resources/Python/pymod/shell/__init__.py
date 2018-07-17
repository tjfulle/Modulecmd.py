from .bash import Bash
from .csh import Csh
from .python import Python
from .shell import Shell

__shells__ = (Shell, Bash, Csh, Python)


def get_shell(shellname):
    """Shell factory method

    Parameters
    ----------
    shellname : str
        The name of the shell

    Returns
    -------
    shell : Shell
        The instantiated shell whose type's name matches shellname

    """
    for shelltype in __shells__:
        if shellname == shelltype.name:
            return shelltype()
    raise Exception('Unknown shell ' + shellname)
