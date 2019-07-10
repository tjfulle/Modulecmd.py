import sys
import pymod.mc
import pymod.modes
import pymod.names
import pymod.error
import pymod.collection
import llnl.util.tty as tty


def save(name):
    """Save currently loaded modules to a collection"""
    loaded_modules = pymod.mc.get_loaded_modules()
    pymod.collection.save(name, loaded_modules)


def show(name):
    """Save the collection `name`"""
    s = pymod.collection.show(name)
    sys.stderr.write(s+'\n')
    return 0


def restore(name):
    """Restore a collection of modules previously saved"""
    the_collection = pymod.collection.get(name)
    if the_collection is None:
        raise pymod.error.CollectionNotFoundError(name)
    return restore_impl(the_collection)


def remove(name):
    """Save currently loaded modules to a collection"""
    pymod.collection.remove(name)


def restore_impl(the_collection):
    # First unload all loaded modules
    pymod.mc.purge(load_after_purge=False)

    # clear the modulepath
    path = pymod.modulepath.Modulepath([])
    pymod.modulepath.set_path(path)

    # Now load the collection, one module at a time
    for (directory, archives) in the_collection:
        pymod.mc.use(directory, append=True)
        for ar in archives:
            try:
                module = pymod.mc.unarchive_module(ar)
                tty.verbose('Loading part of collection: {0}'.format(module))
            except pymod.error.ModuleNotFoundError:
                raise pymod.error.CollectionModuleNotFoundError(ar['fullname'],
                                                                ar['filename'])
            pymod.mc.load_impl(module)
            module.acquired_as = module.fullname
            assert module.is_loaded
    return None
