import pymod.config


class ModuleNotFoundError(Exception):
    def __init__(self, modulename, mp=None):
        msg = '{0!r} is not a module.  See {1!r}.'.format(
            modulename, 'module avail')
        if mp:
            candidates = mp.candidates(modulename)
            if candidates:
                msg += '\n\nDid you mean one of these?'
                msg += '\n\t{0}'.format('\t'.join(candidates))
        super(ModuleNotFoundError, self).__init__(msg)


class FamilyLoadedError(Exception):
    pass


class InconsistentModuleStateError(Exception):  # pragma: no cover
    def __init__(self, module):
        m = 'An inconsistent state occurred when trying to load module\n' \
            '{0!r} that resulted in it not being found on MODULEPATH.\n'  \
            'This is probably due to a module modifying MODULEPATH and\n' \
            'causing automatic changes in loaded/unloaded modules'
        msg = m.format(module.fullname)
        super(InconsistentModuleStateError, self).__init__(msg)


class ModuleConflictError(Exception):
    def __init__(self, loaded, other):
        m = 'Module {other!r} conflicts with loaded module {loaded!r}. Set\n' \
            'environment variable {envar}=1 to let pymod resolve conflicts.'
        msg = m.format(loaded=loaded, other=other,
                       envar=pymod.names.resolve_conflicts)
        super(ModuleConflictError, self).__init__(msg)


class PrereqMissingError(Exception):
    def __init__(self, *missing):
        names = ', '.join(missing)
        if len(missing) > 1:
            msg = 'One of the prerequisites {0!r} must first be loaded'
        else:
            msg = 'Prerequisite {0!r} must first be loaded'
        super(PrereqMissingError, self).__init__(msg.format(names))


class CollectionNotFoundError(Exception):
    def __init__(self, name):
        msg = 'Collection {0!r} does not exist'.format(name)
        super(CollectionNotFoundError, self).__init__(msg)


class CollectionModuleNotFoundError(Exception):
    def __init__(self, name, filename):
        msg = 'Saved module {0!r} does not exist ({1})'.format(name, filename)
        super(CollectionModuleNotFoundError, self).__init__(msg)


class ModuleNotLoadedError(Exception):
    def __init__(self, module):
        superini = super(ModuleNotLoadedError, self).__init__
        msg = 'Unexepecedly unloaded module {}'.format(module)
        superini(msg)


class ModuleLoadError(Exception):
    pass
