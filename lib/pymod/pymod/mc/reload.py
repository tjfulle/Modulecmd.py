import pymod.mc
import pymod.modulepath
import llnl.util.tty as tty
from pymod.error import ModuleNotFoundError


def reload(name):
    """Reload the module given by `modulename`"""
    module = pymod.modulepath.get(name)
    if module is None:
        raise ModuleNotFoundError(name, pymod.modulepath)
    if not module.is_loaded:
        tty.warn("{0} is not loaded!".format(module.fullname))
        return
    assert module.is_loaded
    pymod.mc.swap_impl(module, module, maintain_state=True, caller="reload")
    return module
