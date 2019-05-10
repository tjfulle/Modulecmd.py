import pymod.mc
import pymod.modes
import llnl.util.tty as tty


def purge(load_after_purge=True):
    """Purge all modules from environment"""
    loaded_modules = pymod.mc.get_loaded_modules()
    for module in loaded_modules[::-1]:
        if module.is_loaded:
            print('here i am a.0', module)
            pymod.mc.unload_impl(module)

    if load_after_purge:
        load_after_purge = pymod.config.get('load_after_purge')
        tty.debug(str(load_after_purge))
        if load_after_purge is not None:
            for name in load_after_purge:
                pymod.mc.load(name)

    return None
