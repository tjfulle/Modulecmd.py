import pymod.mc
import pymod.modes
import pymod.modulepath
import llnl.util.tty as tty


def unload(name, tolerant=False):
    """Unload the module given by `name`"""
    module = pymod.modulepath.get(name)
    if module is not None and module.is_loaded:
        pymod.mc.execmodule(module, pymod.modes.unload)
        return None

    # Module is not loaded!
    msg = 'Requesting to unload {0}, but {0} is not loaded'.format(name)
    if module is None:
        # and modulename is not a module!
        msg += ' (nor is it a module)'
    tty.warning(msg)
    return None
