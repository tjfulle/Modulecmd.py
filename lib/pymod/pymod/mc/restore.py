import pymod.mc
import pymod.modes
import pymod.names
import pymod.collection
import llnl.util.tty as tty


def restore(name):
    """Restore a collection of modules previously saved"""

    if name == 'system':
        name = pymod.names.default_sys_collection

    collection = pymod.collection.get(name)
    if collection is None:
        if name == pymod.names.default_sys_collection:
            msg = 'System default collection does not exist'
        else:
            msg = 'Collection {0!r} does not exist'.format(name)
        tty.warn(msg)
        return None

    # First unload all loaded modules
    pymod.mc.purge(load_after_purge=False)
    loaded_modules = pymod.mc.get_loaded_modules()
    for module in loaded_modules[::-1]:
        pymod.mc.execmodule(module, pymod.modes.unload)

    # Now load the collection, one module at a time
    for (directory, modules) in collection:
        pymod.mc.use(directory, append=True)
        for (fullname, filename, opts) in modules:
            module = pymod.modulepath.get(filename)
            if module is None:
                raise CollectionModuleNotFoundError(fullname, filename)
            module.opts = opts
            pymod.mc.load_impl(module)
    return None


class CollectionModuleNotFoundError(Exception):
    def __init__(self, name, filename):
        msg = 'Saved module {0!r} does not exist ({1})'.format(name, filename)
        super(CollectionModuleNotFoundError, self).__init__(msg)
