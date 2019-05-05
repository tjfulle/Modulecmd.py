import contrib.util.logging as logging
from pymod.error import ModuleNotFoundError


def swap(module_a_name, module_b_name):
    """Swap modules a and b"""
    module_a = self.modulepath.get_module_by_name(module_a_name)
    module_b = self.modulepath.get_module_by_name(module_b_name)
    if module_a is None:
        raise ModuleNotFoundError(module_a_name, self.modulepath)
    if module_b is None:
        raise ModuleNotFoundError(module_b_name, self.modulepath)
    if not module_a.is_loaded:
        logging.warn('{0} is not loaded, swap not performed!'.format(
            module_a.fullname))
        return
    if module_b.is_loaded:
        logging.warn('{0} is already loaded!'.format(module_b.fullname))
        return
    assert module_a.is_loaded
    swap_impl(module_a, module_b)

    self.m_state_changed.setdefault('Swapped', []).append(
        [module_a.fullname, module_b.fullname])
    return None


def swap_impl(module_a, module_b, options_b=None, maintain_state=0):
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
    loaded = self.get_loaded_modules()
    for (i, other) in enumerate(loaded):
        if other.name == module_a.name:
            # All modules coming after this one will be unloaded and
            # reloaded
            to_unload_and_reload = loaded[i:]
            break
    else:
        raise Exception('Should have found module_a to swap')

    # Unload any that need to be unloaded first
    my_opts = {}
    for other in to_unload_and_reload[::-1]:
        my_opts[other.fullname] = self.environ.get_loaded_modules('opts', module=other)
        self.execmodule(UNLOAD, other)
    assert other.name == module_a.name

    # Now load it
    if options_b:
        self.set_moduleopts(module_b, options_b)
    self.execmodule(LOAD, module_b)

    # Reload any that need to be unloaded first
    for other in to_unload_and_reload[1:]:
        if maintain_state:
            this_module = self.modulepath.get_module_by_filename(other.filename)
        else:
            this_module = self.modulepath.get_module_by_name(other.fullname)
        if this_module is None:
            m_tmp = self.modulepath.get_module_by_name(other.name)
            if m_tmp is not None:
                this_module = m_tmp
            else:
                # The only way this_module is None is if a swap of modules
                # caused a change to MODULEPATH making this module
                # unavailable.
                on_mp_changed = self.m_state_changed.setdefault('MP', {})
                on_mp_changed.setdefault('U', []).append(other)
                continue

        if this_module.filename != other.filename:
            on_mp_changed = self.m_state_changed.setdefault('MP', {})
            on_mp_changed.setdefault('Up', []).append((other, this_module))

        # Check for module options to set.  If they were not explicitly set
        # on the command line, set them from the previously loaded version
        if not self.moduleopts.get(this_module.fullname):
            self.moduleopts[this_module.fullname] = my_opts[other.fullname]
        self.execmodule(LOAD, this_module)

    return module_b
