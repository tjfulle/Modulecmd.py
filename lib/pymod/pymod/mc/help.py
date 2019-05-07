import sys

import pymod.modes
import pymod.modulepath
from pymod.mc.execmodule import execmodule_in_sandbox
from pymod.error import ModuleNotFoundError


def help(modulename):
    """Display 'help' message for the module given by `modulename`"""
    module = pymod.modulepath.get(modulename)
    if module is None:
        raise ModuleNotFoundError(modulename, mp=pymod.modulepath)
    execmodule_in_sandbox(module, pymod.modes.help)
    s = module.format_help()
    sys.stderr.write(s + '\n')
