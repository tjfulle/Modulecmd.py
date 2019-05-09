import pymod.mc
import pymod.modes


def refresh():
    """Purge all modules from environment"""
    loaded_modules = pymod.mc.get_loaded_modules()
    for module in loaded_modules[::-1]:
        pymod.mc.execmodule(module, pymod.modes.unload)
    for module in loaded_modules:
        pymod.mc.execmodule(module, pymod.modes.load)
