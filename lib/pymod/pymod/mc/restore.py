import pymod.mc
import pymod.modes
import pymod.names
import pymod.collection
import contrib.util.logging as logging


def restore(name, warn_if_missing=True):
    """Restore a collection of modules previously saved"""

    if name == 'system':
        name = pymod.names.default_sys_collection

    collection = pymod.collection.get(name)
    if collection is None:
        if warn_if_missing:
            if name == pymod.names.default_sys_collection:
                msg = 'System default collection does not exist'
            else:
                msg = 'Collection {0!r} does not exist'.format(name)
            logging.warn(msg)
        return None

    # First unload all loaded modules
    loaded_modules = pymod.mc.get_loaded_modules()
    for module in loaded_modules[::-1]:
        pymod.mc.execmodule(module, pymod.modes.unload)

    # Now load the collection, one module at a time
    for (directory, modules) in collection:
        pymod.mc.use(directory, append=True)
        for (fullname, filename, opts) in modules:
            module = pymod.modulepath.get(filename)
            if module is None:
                logging.error(
                    'Saved module {0!r} does not exist ({1})'
                    .format(m_dict['name'], m_dict['filename']))
            module.opts = opts
            pymod.mc.execmodule(module, pymod.modes.load)
    return None
