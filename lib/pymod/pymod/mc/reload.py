import pymod.mc
import pymod.modulepath
import llnl.util.tty as tty
from pymod.error import ModuleNotFoundError


def reload(name):
    """Reload the module given by `modulename`"""
    module = pymod.modulepath.get(name)
    if module is None:
        raise ModuleNotFoundError(modulename, self.modulepath)
    if not module.is_loaded:
        tty.warn('{0} is not loaded!'.format(module.fullname))
        return
    assert module.is_loaded
    pymod.mc.swap(module, module, maintain_state=1)
    return module
