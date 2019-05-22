import pymod.mc
from pymod.error import PrereqMissingError


def _partition(key):
    first, _, last = key.partition(':')
    if not last.split():
        first, last = 'name', first
    elif first not in ('family', 'name'):
        raise Exception('{0} not a known ID to prereq'.format(first))
    return first, last


def prereq_any(*prereqs):
    loaded_modules = pymod.mc.get_loaded_modules()
    lm_names = [x for m in loaded_modules for x in [m.name, m.fullname]]
    lm_fams = [m.family for m in loaded_modules if m.family]
    for prereq in prereqs:
        key, val = _partition(prereq)
        a = lm_fams if key == 'family' else lm_names
        if val in a:
            return
    raise PrereqMissingError(*prereqs)


def prereq(*prereqs):
    loaded_modules = pymod.mc.get_loaded_modules()
    lm_names = [x for m in loaded_modules for x in [m.name, m.fullname]]
    lm_fams = [m.family for m in loaded_modules if m.family]
    for prereq in prereqs:
        key, val = _partition(prereq)
        a = lm_fams if key == 'family' else lm_names
        if val in a:
            continue
        raise PrereqMissingError(val)
