import pymod.mc
import pymod.modes
import pymod.names
import pymod.error
import pymod.collection


def restore(name):
    """Restore a collection of modules previously saved"""

    collection = pymod.collection.get(name)
    if collection is None:
        raise pymod.error.CollectionNotFoundError(name)

    return restore_impl(collection)


def restore_impl(collection):
    # First unload all loaded modules
    pymod.mc.purge(load_after_purge=False)
    loaded_modules = pymod.mc.get_loaded_modules()
    for module in loaded_modules[::-1]:
        pymod.mc.unload_impl(module)

    # clear the modulepath
    pymod.modulepath.clear()

    # Now load the collection, one module at a time
    for (directory, modules) in collection:
        pymod.mc.use(directory, append=True)
        for (fullname, filename, opts) in modules:
            module = pymod.modulepath.get(filename)
            if module is None:
                raise pymod.error.CollectionModuleNotFoundError(fullname, filename)
            module.opts = opts
            pymod.mc.load_impl(module)
    return None
