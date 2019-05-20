import pymod.mc
from pymod.error import PrereqMissingError


def prereq_any(*prereqs):
    loaded_modules = pymod.mc.get_loaded_modules()
    lm_names = [x for m in loaded_modules for x in [m.name, m.fullname]]
    for name in prereqs:
        if name in lm_names:
            return
    raise PrereqMissingError(*prereqs)


def prereq(*prereqs):
    loaded_modules = pymod.mc.get_loaded_modules()
    lm_names = [x for m in loaded_modules for x in [m.name, m.fullname]]
    for name in prereqs:
        if name in lm_names:
            continue
        raise PrereqMissingError(name)
