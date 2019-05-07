import pymod.mc
import pymod.modes
import pymod.modulepath

from pymod.mc.execmodule import execmodule
from pymod.error import ModuleNotFoundError
import llnl.util.tty as tty


def load(modulename, opts=None, do_not_register=False, insert_at=None,
         increment_refcnt_if_loaded=False):
    """Load the module given by `modulename`"""

    tty.verbose('Loading {}'.format(modulename))

    # Execute the module
    module = pymod.modulepath.get(modulename)
    if module is None:
        # is it a collection?
        if pymod.collections.is_collection(modulename):
            return pymod.collections.restore(modulename)
        else:
            raise ModuleNotFoundError(modulename, mp=pymod.modulepath)

    # Set the command line options
    module.opts = opts

    if module.is_loaded:
        if increment_refcnt_if_loaded:
            pymod.mc.increment_refcount(module)
        else:
            msg = '{0} is already loaded, use {1!r} to load again'
            tty.warn(msg.format(module.fullname, 'module reload'))
        return 0

    if insert_at is None:
        return load_impl(module, do_not_register=do_not_register)

    return load_inserted(module, insert_at,
                         do_not_register=do_not_register)


def load_inserted(module, insert_at, do_not_register=False):
    """Load the `module` at `insert_at` by unloading all modules beyond
    `insert_at`, loading `module`, then reloading the unloaded modules"""

    raise NotImplementedError('trying to load {0} but mc.load_inserted is '
                              'not yet implemented'.format(module))

    module_opts = {}
    loaded_modules = pymod.mc.get_loaded_modules()
    to_unload_and_reload = loaded_modules[(insert_at)-1:]
    for other in to_unload_and_reload[::-1]:
        module_opts[other.fullname] = other.opts
        execmodule(other, pymod.modes.unload)

    return_module = load_impl(module, do_not_register=do_not_register)

    # Reload any that need to be unloaded first
    for other in to_unload_and_reload:
        this_module = pymod.modulepath.get(other.filename)
        if this_module is None:
            m_tmp = pymod.modulepath.get(other.name)
            if m_tmp is not None:
                this_module = m_tmp
            else:
                # The only way this_module is None is if inserting
                # caused a change to MODULEPATH making this module
                # unavailable.
                pymod.mc.unloaded_on_mp_change(other)
                continue

        if this_module.filename != other.filename:
            pymod.mc.swapped_on_mp_change(other, this_module)

        this_opts = this_module.opts or module_opts[this_module.fullname]
        execmodule(this_module, pymod.modes.load,
                   do_not_register=do_not_register)

    return return_module

def load_impl(module, do_not_register=False):
    """Load the module given by `modulename`"""

    # Before loading this module, look for module of same name and unload
    # it if necessary

    # See if a module of the same name is already loaded. If so, swap that
    # module with the requested module
    for (i, other) in enumerate(pymod.mc.get_loaded_modules()):
        if other.name == module.name:
            pymod.mc.swap_impl(other, module)
            pymod.mc.swapped_on_version_change(other, module)
            return module

    # Now load it
    execmodule(module, pymod.modes.load, do_not_register=do_not_register)

    return module
