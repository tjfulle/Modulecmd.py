import pymod.mc
import llnl.util.tty as tty

def conflict(mode, module, *others):
    loaded_modules = pymod.mc.get_loaded_modules()
    lm_names = [x for m in loaded_modules for x in [m.name, m.fullname]]
    for other in others:
        if other.name in lm_names or other.fullname in lm_names:
            if pymod.config.get('resolve_conflicts'):
                # Unload the conflicting module
                pymod.mc.unload(other.filename)
            else:
                msg  = 'Module {name!r} conflicts with loaded module '
                msg += '{modulename!r}. Set environment variable '
                msg += 'PYMOD_RESOLVE_CONFLICTS=1 to let pymod resolve '
                msg += 'conflicts.'
                tty.die(msg.format(name=module.name, modulename=other.name))
