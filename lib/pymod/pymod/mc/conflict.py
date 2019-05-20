import pymod.mc
from pymod.error import ModuleConflictError

def conflict(module, *conflicting):
    """The module we are trying to load, `module` conflicts with the module
    given by `conflicting_module`"""
    loaded_modules = pymod.mc.get_loaded_modules()
    lm_names = list(set([x for m in loaded_modules for x in [m.name, m.fullname]]))
    for other in conflicting:
        if other in lm_names:
            if pymod.config.get('resolve_conflicts'):
                # Unload the conflicting module
                pymod.mc.unload(other)
            else:
                raise ModuleConflictError(other, module.name)
