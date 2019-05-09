import sys

import pymod.modes
import pymod.modulepath
from pymod.mc.execmodule import execmodule_in_sandbox
from pymod.error import ModuleNotFoundError


def whatis(modulename):
    """Display 'whatis' message for the module given by `modulename`"""
    module = pymod.modulepath.get(modulename)
    if module is None:
        raise ModuleNotFoundError(modulename, mp=pymod.modulepath)
    execmodule_in_sandbox(module, pymod.modes.whatis)
    s = module.format_whatis()
    sys.stderr.write(s + '\n')
