import pymod.mc
import pymod.modes
import pymod.modulepath
from pymod.error import ModuleNotFoundError


def help(modulename):
    """Display 'help' message for the module given by `modulename`"""
    module = pymod.modulepath.get(modulename)
    if module is None:
        raise ModuleNotFoundError(modulename, mp=pymod.modulepath)
    pymod.mc.load_partial(module, mode=pymod.modes.help)
    return module.format_help()
