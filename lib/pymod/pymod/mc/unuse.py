import os
import pymod.mc
import pymod.modes
import pymod.modulepath


def unuse(dirname):
    """Remove dirname from MODULEPATH"""

    dirname = os.path.expanduser(dirname)
    if not pymod.modulepath.contains(dirname):
        # Nothing to do!
        return

    # load them to initialize list of loaded modules
    _ = pymod.mc.get_loaded_modules()

    # Now remove dirname from MODULEPATH
    popped_modules = pymod.modulepath.remove_path(dirname)
    orphaned = determine_swaps_due_to_removal(popped_modules)

    # Unload orphans
    for orphan in orphaned[::-1]:
        pymod.mc.unload_impl(orphan[0])

    # Load modules bumped by removal of dirname from MODULEPATH
    for orphan in orphaned:
        if orphan[1] is None:
            # No longer available!
            pymod.mc.unloaded_on_mp_change(orphan[0])
        else:
            pymod.mc.load_impl(orphan[1])
            pymod.mc.swapped_on_mp_change(orphan[0], orphan[1])


def determine_swaps_due_to_removal(popped_modules):
    """Determine with of the popped modules should be swapped for modules that
    became available after removing a directory from the modulepath

    Parameters
    ----------
    popped_modules : list of Module
        Modules no longer available due to their modulepath being removed

    Return
    ------
    orphans : list of tuple
        orphans[i][0] loaded module left orphaned
        orphans[i][1] module to be loaded in its place, or None

    """

    # Determine which modules may have moved up in priority due to removal
    # of directory from path. If they have the same name as an orphan, it
    # will be loaded in the orphans place
    orphaned = [m for m in popped_modules if m.is_loaded]
    for (i, orphan) in enumerate(orphaned):
        for attr in ("fullname", "name"):
            other = pymod.modulepath.get(getattr(orphan, attr))
            if other is not None:
                orphaned[i] = (orphan, other)
                break
        else:
            orphaned[i] = (orphan, None)
    return orphaned
