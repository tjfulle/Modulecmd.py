import os
import pymod.modes
import pymod.modulepath


def unuse(dirname):
    """Remove dirname from MODULEPATH"""

    if dirname.startswith('~'):
        dirname = os.path.expanduser(dirname)

    if not pymod.modulepath.contains(dirname):
        # Nothing to do!
        return

    # Now remove dirname from MODULEPATH
    _, orphaned, bumped = pymod.modulepath.remove_path(dirname)

    # Unload orphans
    for orphan in orphaned[::-1]:
        pymod.mc.execmodule(orphan, pymod.modes.unload)

    # Load modules bumped by removal of dirname from MODULEPATH
    for (i, orphan) in orphaned:
        if bumped[i] is None:
            # No longer available!
            pymod.mc.unloaded_on_mp_change(orphan)
        else:
            pymod.mc.execmodule(bumped[i], pymod.modes.load)
            pymod.mc.swapped_on_mp_change(orphan, bumped[i])

    return None