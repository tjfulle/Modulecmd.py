import sys

import pymod.modulepath
from pymod.mc.execmodule import execmodule_in_sandbox
from pymod.error import ModuleNotFoundError
from contrib.util.logging import terminal_size


def whatis(modulename):
    """Display 'whatis' message for the module given by `modulename`"""
    module = pymod.modulepath.get(modulename)
    if module is None:
        raise ModuleNotFoundError(modulename, mp=pymod.modulepath)
    execmodule_in_sandbox(module, 'whatis')
    _, width = terminal_size()
    x = " " + module.name + " "
    s = '{0}'.format(x.center(width, '=')) + '\n'
    s += module.whatis + '\n'
    s += '=' * width
    sys.stderr.write(s + '\n')
