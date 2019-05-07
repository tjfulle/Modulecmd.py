import pymod.mc
import llnl.util.tty as tty


def prereq_any(mode, *names):
    loaded_modules = pymod.mc.get_loaded_modules()
    lm_names = [x for m in loaded_modules for x in [m.name, m.fullname]]
    for name in names:
        if name in lm_names:
            return
    tty.die('One of the prerequisites {0!r} must first be loaded'.format(names))


def prereq(mode, *names):
    loaded_modules = pymod.mc.get_loaded_modules()
    lm_names = [x for m in loaded_modules for x in [m.name, m.fullname]]
    for name in names:
        if name in lm_names:
            continue
        tty.die('Prerequisite {0!r} must first be loaded'.format(name))
