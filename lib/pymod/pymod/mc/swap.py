import pymod.mc
import pymod.modes
import pymod.modulepath
import llnl.util.tty as tty
from pymod.error import ModuleNotFoundError


def swap(module_a_name, module_b_name, caller="command_line"):
    """Swap modules a and b"""
    module_a = pymod.modulepath.get(module_a_name)
    module_b = pymod.modulepath.get(module_b_name)
    if module_a is None:
        raise ModuleNotFoundError(module_a_name, pymod.modulepath)
    if module_b is None:
        raise ModuleNotFoundError(module_b_name, pymod.modulepath)
    if module_b.is_loaded:
        tty.warn("{0} is already loaded!".format(module_b.fullname))
        return module_b
    if not module_a.is_loaded:
        return pymod.mc.load_impl(module_b)

    assert module_a.is_loaded

    swap_impl(module_a, module_b, caller=caller)

    pymod.mc.swapped_explicitly(module_a, module_b)

    return module_b


def swap_impl(module_a, module_b, maintain_state=False, caller="command_line"):
    """The general strategy of swapping is to unload all modules in reverse
    order back to the module to be swapped.  That module is then unloaded
    and its replacement loaded.  Afterward, modules that were previously
    unloaded are reloaded.

    On input:
        module_a is loaded
        module_b is not loaded

    On output:
        module_a is not loaded
        module_b is loaded

    The condition that module_b is not loaded on input is not strictly true
    In the case that a module is reloaded, module_a and module_b would be
    the same, so module_b would also be loaded.

    """

    assert module_a.is_loaded

    # Before swapping, unload modules and later reload
    loaded = pymod.mc.get_loaded_modules()
    opts = dict([(m.name, m.opts) for m in loaded])
    for (i, other) in enumerate(loaded):
        if other.name == module_a.name:
            # All modules coming after this one will be unloaded and
            # reloaded
            to_unload_and_reload = loaded[i:]
            break
    else:  # pragma: no cover
        raise NoModulesToSwapError

    # Unload any that need to be unloaded first
    for other in to_unload_and_reload[::-1]:
        pymod.mc.unload_impl(other, caller=caller)
    assert other.name == module_a.name

    # Now load it
    pymod.mc.load_impl(module_b)

    # Reload any that need to be unloaded first
    for other in to_unload_and_reload[1:]:
        if maintain_state:
            this_module = pymod.modulepath.get(other.filename)
        else:
            this_module = pymod.modulepath.get(other.acquired_as)
        if this_module is None:
            # The only way this_module is None is if a swap of modules
            # caused a change to MODULEPATH making this module
            # unavailable.
            pymod.mc.unloaded_on_mp_change(other)
            continue

        if this_module.filename != other.filename:
            pymod.mc.swapped_on_mp_change(other, this_module)

        # Now load the thing
        this_module.opts = opts.get(this_module.name, this_module.opts)
        pymod.mc.load_impl(this_module)

    return module_b


class NoModulesToSwapError(Exception):
    pass
