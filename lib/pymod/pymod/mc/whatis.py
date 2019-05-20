import pymod.mc
import pymod.modes
import pymod.modulepath
from pymod.error import ModuleNotFoundError


def whatis(name):
    """Display 'whatis' message for the module given by `name`"""
    module = pymod.modulepath.get(name)
    if module is None:
        raise ModuleNotFoundError(name, mp=pymod.modulepath)
    pymod.mc.load_partial(module, mode=pymod.modes.whatis)
    return module.format_whatis()
