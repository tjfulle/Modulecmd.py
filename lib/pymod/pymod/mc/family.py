import pymod.names
import pymod.modes
import pymod.environ

def family(mode, module, family_name):
    """Assign a family"""

    name = module.name
    version = module.version
    module.family = family_name
    def family_envar_keys():
        fam_key = pymod.names.family_name(family_name)
        ver_key = pymod.names.family_version(family_name)
        return (fam_key, ver_key)

    if mode in (pymod.modes.load,):
        fam_key, ver_key = family_envar_keys()
        fam = pymod.environ.get(fam_key)
        if fam is not None:
            # Attempting to load module of same family
            ver = pymod.environ.get(ver_key)
            other = fam if ver in ('false', None) else os.path.join(fam, ver)
            raise FamilyLoadedError(other)

        pymod.environ.set(fam_key, name)
        ver = 'false' if not version.string else version.string
        pymod.environ.set(ver_key, ver)

    elif mode in (pymod.modes.unload,):
        fam_key, ver_key = family_envar_keys()
        pymod.environ.unset(fam_key)
        pymod.environ.unset(ver_key)
