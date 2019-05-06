import pymod.mc
import pymod.modes


def purge(load_after_purge=True):
    """Purge all modules from environment"""
    loaded_modules = pymod.mc.get_loaded_modules()
    for module in loaded_modules[::-1]:
        pymod.mc.execmodule(module, pymod.modes.unload)

    if load_after_purge:
        load_after_purge = pymod.config.get('load_after_purge')
        if load_after_purge is not None:
            for name in load_after_purge:
                pymod.mc.load(name)

    return None
