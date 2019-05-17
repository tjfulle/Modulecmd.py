import os
import pymod.mc
import pymod.modulepath


def use(dirname, append=False, delete=False):
    """Add dirname to MODULEPATH"""
    dirname = os.path.expanduser(dirname)
    if delete:
        pymod.mc.unuse(dirname)
        return
    elif append:
        pymod.modulepath.append_path(dirname)
    else:
        prepended_modules = pymod.modulepath.prepend_path(dirname)
        bumped = determine_swaps_due_to_prepend(prepended_modules)
        for (old, new) in bumped:
            assert old.is_loaded
            pymod.mc.swap_impl(old, new)
            pymod.mc.swapped_on_mp_change(old, new)


def determine_swaps_due_to_prepend(prepended_modules):
    """Determine with modules lost precedence and need to be replaced

    Parameters
    ----------
    prepended_modules : list of Module
        These are modules that are now available from prepending their
        modulepath to pymod.modulepath

    Returns
    -------
    bumped : list of Module
        List of loaded modules that have lower precedence than a module of the
        same name in prepended_modules. These should be swapped

    """
    # Determine which modules changed in priority due to insertion of new
    # directory in to path
    bumped = []
    loaded_modules = pymod.mc.get_loaded_modules()

    # Check for fullname first
    fullnames = [m.fullname for m in prepended_modules]
    for (i, module) in enumerate(loaded_modules):
        if module.fullname not in fullnames:
            continue
        prepended_module = prepended_modules[fullnames.index(module.fullname)]
        if prepended_module.filename != module.filename:
            # The new module has the same name, but different filename. Since
            # new module has higher precedence (since its path was prepended to
            # modulepath), we swap them
            bumped.append((module, prepended_module))
            loaded_modules[i] = None

    names = [m.name for m in prepended_modules]
    for (i, module) in enumerate(loaded_modules):
        if module is None or module.name not in names:
            continue
        prepended_module = prepended_modules[names.index(module.name)]
        if prepended_module.filename != module.filename:
            bumped.append((module, prepended_modules[i]))

    return bumped
