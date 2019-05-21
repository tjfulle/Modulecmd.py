import pymod.mc
import pymod.collection


def remove(name):
    """Save currently loaded modules to a collection"""
    pymod.collection.remove(name)
