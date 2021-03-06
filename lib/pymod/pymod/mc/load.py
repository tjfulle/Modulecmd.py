import pymod.mc
import pymod.modes
import pymod.names
import pymod.environ
import pymod.modulepath
import pymod.collection

from pymod.mc.execmodule import execmodule
from pymod.error import ModuleNotFoundError, ModuleLoadError
import llnl.util.tty as tty


def load(name, opts=None, insert_at=None, caller="command_line"):
    """Load the module given by `name`

    This is a higher level interface to `load_impl` that gets the actual module
    object from `name`

    Parameters
    ----------
    name : string_like
        Module name, full name, or file path
    opts : dict
        (Optional) options to send to module
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
    tty.verbose("Loading {0}".format(name))

    # Execute the module
    module = pymod.modulepath.get(name, use_file_modulepath=True)  # caller=="command_line")
    if module is None:
        if caller == "command_line":
            collection = pymod.collection.get(name)
            if collection is not None:
                return pymod.mc.collection.restore_impl(name, collection)
        raise ModuleNotFoundError(name, mp=pymod.modulepath)

    # Set the command line options
    if opts:
        module.opts = opts

    if module.is_loaded:
        if caller == "modulefile":
            pymod.mc.increment_refcount(module)
        else:
            tty.warn(
                "{0} is already loaded, use 'module reload' to reload".format(
                    module.fullname
                )
            )
        return module

    if pymod.environ.get(pymod.names.loaded_collection):  # pragma: no cover
        collection = pymod.environ.get(pymod.names.loaded_collection)
        tty.debug(
            "Loading {0} on top of loaded collection {1}. "
            "Removing the collection name from the environment".format(
                module.fullname, collection
            )
        )
        pymod.environ.unset(pymod.names.loaded_collection)

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

    if getattr(module, "exec_failed_do_not_register", False):
        # Something happened during the execution of this module and we are not
        # to register it.
        pass
    elif module.refcount != 0:
        # Nonzero reference count means the module load was completed by
        # someone else. This can only happen in the case of loading a module of
        # the same family. In that case, execmodule catches a FamilyLoadedError
        # exception and swaps this module with the module of the same family.
        # The swap completes the load.
        if not (
            pymod.mc._mc._swapped_on_family_update
            and module == pymod.mc._mc._swapped_on_family_update[-1][1]
        ):  # pragma: no cover
            raise ModuleLoadError("Expected 0 refcount")
    else:
        pymod.mc.register_module(module)

    return


def load_inserted_impl(module, insert_at):
    """Load the `module` at `insert_at` by unloading all modules beyond
    `insert_at`, loading `module`, then reloading the unloaded modules"""

    insertion_loc = insert_at - 1
    loaded_modules = pymod.mc.get_loaded_modules()
    to_unload_and_reload = loaded_modules[insertion_loc:]
    opts = [m.opts for m in to_unload_and_reload]
    for other in to_unload_and_reload[::-1]:
        pymod.mc.unload_impl(other)

    load_impl(module)

    # Reload any that need to be unloaded first
    for (i, other) in enumerate(to_unload_and_reload):
        assert not other.is_loaded
        other_module = pymod.modulepath.get(other.acquired_as)
        if other_module is None:
            # The only way this_module is None is if inserting caused a change
            # to MODULEPATH making this module unavailable.
            pymod.mc.unloaded_on_mp_change(other)
            continue

        if other_module.filename != other.filename:
            pymod.mc.swapped_on_mp_change(other, other_module)
        else:
            other_module.opts = opts[i]

        load_impl(other_module)

    return


def load_partial(module, mode=None):
    """Implementation of load, but only load partially.

    Parameters
    ----------
    module : Module
        The module to load

    Notes
    -----
    This function is used to do a partial load. A partial load is one in which
    only some of the callback functions are actually executed. This function is
    used, e.g., by restore_clone to load a module, but only execute set_alias
    and set_shell_function.  In fact, that is the only current use case.

    """
    # Execute the module
    if mode is not None:
        assert mode in pymod.modes.informational
    mode = mode or pymod.modes.load_partial
    execmodule(module, mode)
    return
