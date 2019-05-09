import pymod.mc
import pymod.modes
import pymod.modulepath

from pymod.mc.execmodule import execmodule
from pymod.error import ModuleNotFoundError
import llnl.util.tty as tty


def load(name, opts=None, insert_at=None, caller='command_line'):
    """Load the module given by `name`

    This is a higher level interface to `load_impl` that gets the actual module
    object from `name`

    Parameters
    ----------
    name : string_like
        Module name, full name, or file path
    insert_at : int
        Load the module as the `insert_at`th module.
    caller : str
        Who is calling. If modulefile, the reference count will be incremented
        if the module is already loaded.

    Returns
    -------
    module : Module
        If the `name` was loaded (or is already loaded), return its module.

    Raises
    ------
    ModuleNotFoundError

    """
    tty.verbose('Loading {}'.format(name))

    # Execute the module
    module = pymod.modulepath.get(name)
    if module is None:
        raise ModuleNotFoundError(name, mp=pymod.modulepath)

    # Set the command line options
    if opts:
        module.opts = opts

    if module.is_loaded:
        if caller == 'modulefile':
            pymod.mc.increment_refcount(module)
        else:
            tty.warn('{0} is already loaded, use \'module reload\' to reload'
                     .format(module.fullname))
        return module

    if insert_at is not None:
        load_inserted_impl(module, insert_at)
    else:
        load_impl(module)

    return module


def load_impl(module):
    """Implementation of load.

    Parameters
    ----------
    module : Module
        The module to load

    """
    # See if a module of the same name is already loaded. If so, swap that
    # module with the requested module
    for other in pymod.mc.get_loaded_modules():
        if other.name == module.name:
            pymod.mc.swap_impl(other, module)
            pymod.mc.swapped_on_version_change(other, module)
            return

    # Now load it
    execmodule(module, pymod.modes.load)
    refcount = pymod.mc.get_refcount(module)

    if refcount != 0:
        # Nonzero reference count means the module load was completed by
        # someone else. This can only happen in the case of loading a module of
        # the same family. In that case, execmodule catches a FamilyLoadedError
        # exception and swaps this module with the module of the same family.
        # The swap completes the load.
        if not (pymod.mc._mc._swapped_on_family_update and
                module == pymod.mc._mc._swapped_on_family_update[-1][1]):
            raise ModuleLoadError('Expected 0 ref_count')
    else:
        pymod.mc.on_module_load(module)

    return


def load_inserted_impl(module, insert_at):
    """Load the `module` at `insert_at` by unloading all modules beyond
    `insert_at`, loading `module`, then reloading the unloaded modules"""

    loaded_modules = pymod.mc.get_loaded_modules()
    to_unload_and_reload = loaded_modules[(insert_at)-1:]
    for other in to_unload_and_reload[::-1]:
        pymod.mc.unload_impl(other)

    load_impl(module)

    # Reload any that need to be unloaded first
    for other in to_unload_and_reload:
        other_module = pymod.modulepath.get(other.filename)
        if other_module is None:
            m_tmp = pymod.modulepath.get(other.name)
            if m_tmp is not None:
                other_module = m_tmp
            else:
                # The only way this_module is None is if inserting
                # caused a change to MODULEPATH making this module
                # unavailable.
                pymod.mc.unloaded_on_mp_change(other)
                continue

        if other_module.filename != other.filename:
            pymod.mc.swapped_on_mp_change(other, other_module)

        load_impl(other_module)

    return


class ModuleLoadError(Exception):
    pass
