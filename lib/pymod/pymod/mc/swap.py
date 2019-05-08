import pymod.mc
import pymod.modes
import pymod.modulepath
import llnl.util.tty as tty
from pymod.error import ModuleNotFoundError


def swap(module_a_name, module_b_name, maintain_state=False):
    """Swap modules a and b"""
    module_a = pymod.modulepath.get(module_a_name)
    module_b = pymod.modulepath.get(module_b_name)
    if module_a is None:
        raise ModuleNotFoundError(module_a_name, pymod.modulepath)
    if module_b is None:
        raise ModuleNotFoundError(module_b_name, pymod.modulepath)
    if module_b.is_loaded:
        tty.warn('{0} is already loaded!'.format(module_b.fullname))
        return module_b
    if not module_a.is_loaded:
        return pymod.mc.load(module_b)

    assert module_a.is_loaded
    swap_impl(module_a, module_b, maintain_state=maintain_state)

    pymod.mc.swapped_explicitly(module_a, module_b)

    return module_b


def swap_impl(module_a, module_b, maintain_state=False):
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
    for (i, other) in enumerate(loaded):
        if other.name == module_a.name:
            # All modules coming after this one will be unloaded and
            # reloaded
            to_unload_and_reload = loaded[i:]
            break
    else:
        raise NoModulesToSwapError

    # Unload any that need to be unloaded first
    for other in to_unload_and_reload[::-1]:
        pymod.mc.execmodule(other, pymod.modes.unload)
    assert other.name == module_a.name

    # Now load it
    pymod.mc.execmodule(module_b, pymod.modes.load)

    # Reload any that need to be unloaded first
    for other in to_unload_and_reload[1:]:
        if maintain_state:
            this_module = pymod.modulepath.get(other.filename)
        else:
            this_module = pymod.modulepath.get(other.fullname)
        if this_module is None:
            m_tmp = pymod.modulepath.get(other.name)
            if m_tmp is not None:
                this_module = m_tmp
            else:
                # The only way this_module is None is if a swap of modules
                # caused a change to MODULEPATH making this module
                # unavailable.
                pymod.mc.unloaded_on_mp_change(other)
                continue

        if this_module.filename != other.filename:
            pymod.mc.swapped_on_mp_change(other, this_module)

        # Now load the thing
        pymod.mc.execmodule(this_module, pymod.modes.load)

    return module_b


class NoModulesToSwapError(Exception):
    pass
