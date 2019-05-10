import pymod.mc
import llnl.util.tty as tty


def refresh():
    """Unload all modules from environment and reload them"""
    loaded_modules = pymod.mc.get_loaded_modules()
    for module in loaded_modules[::-1]:
        tty.verbose('Unloading {}'.format(module))
        if module.is_loaded:
            pymod.mc.unload_impl(module)
    for module in loaded_modules:
        tty.verbose('Loading {}'.format(module))
        if not module.is_loaded:
            pymod.mc.load_impl(module)
