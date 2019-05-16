import os
import pymod.modes
import pymod.modulepath


def unuse(dirname):
    """Remove dirname from MODULEPATH"""

    dirname = os.path.expanduser(dirname)
    if not pymod.modulepath.contains(dirname):
        # Nothing to do!
        return

    # Now remove dirname from MODULEPATH
    _, orphaned = pymod.modulepath.remove_path(dirname)

    # Unload orphans
    for orphan in orphaned[::-1]:
        pymod.mc.unload_impl(orphan[0])

    # Load modules bumped by removal of dirname from MODULEPATH
    for (i, orphan) in enumerate(orphaned):
        if orphan[1] is None:
            # No longer available!
            pymod.mc.unloaded_on_mp_change(orphan[0])
        else:
            pymod.mc.load_impl(orphan[1])
            pymod.mc.swapped_on_mp_change(orphan[0], orphan[1])
