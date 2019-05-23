import pymod.mc
import pymod.collection


def save(name):
    """Save currently loaded modules to a collection"""
    loaded_modules = pymod.mc.get_loaded_modules()
    pymod.collection.save(name, loaded_modules)
