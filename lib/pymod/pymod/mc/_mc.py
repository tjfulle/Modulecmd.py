import os
from six import StringIO

import pymod.names
import pymod.error
import pymod.module
import pymod.environ
import pymod.modulepath

import llnl.util.tty as tty


_loaded_modules = None
_swapped_explicitly = []
_swapped_on_version_change = []
_swapped_on_family_update = []
_swapped_on_mp_change = []
_unloaded_on_mp_change = []


__all__ = [
    'get_loaded_modules',
    'set_loaded_modules',
    'increment_refcount',
    'decrement_refcount',
    'swapped_explicitly',
    'swapped_on_version_change',
    'swapped_on_family_update',
    'swapped_on_mp_change',
    'unloaded_on_mp_change',
    'register_module',
    'unregister_module',
    'module_is_loaded',
    'archive_module',
    'unarchive_module',
]


def module_is_loaded(key):
    if isinstance(key, pymod.module.Module):
        return key in get_loaded_modules()
    elif os.path.isfile(key):
        return key in [m.filename for m in get_loaded_modules()]
    else:
        for module in get_loaded_modules():
            if module.name == key or module.fullname == key:
                return True
    return False


def get_loaded_modules():
    global _loaded_modules
    if _loaded_modules is None:
        tty.debug('Reading loaded modules')
        _loaded_modules = []
        lm_cellar = pymod.environ.get_deserialized(
            pymod.names.loaded_module_cellar, default=[]
        )
        for ar in lm_cellar:
            module = unarchive_module(ar)
            _loaded_modules.append(module)
    # return copy so that no one else can modify the loaded modules
    return list(_loaded_modules)


def archive_module(module):
    ar = dict(fullname=module.fullname,
              filename=module.filename,
              family=module.family,
              opts=module.opts,
              acquired_as=module.acquired_as,
              refcount=module.refcount,
              modulepath=module.modulepath)
    return ar


def unarchive_module(ar):
    path = ar.get('modulepath')
    if path and not pymod.modulepath.contains(path):  # pragma: no cover
        pymod.mc.use(path)
    module = pymod.modulepath.get(ar['filename'])
    if module is None:
        raise pymod.error.ModuleNotFoundError(ar['fullname'])
    assert module.fullname == ar['fullname']
    module.family = ar['family']
    module.opts = ar['opts']
    module.acquired_as = ar['acquired_as']
    module.refcount = ar['refcount']
    return module


def set_loaded_modules(modules):
    """Set environment variables for loaded module names and files"""
    global _loaded_modules
    _loaded_modules = modules

    assert all([m.acquired_as is not None for m in _loaded_modules])
    lm = [archive_module(m) for m in _loaded_modules]
    pymod.environ.set_serialized(pymod.names.loaded_module_cellar, lm)

    # The following are for compatibility with other module programs
    lm_names = [m.fullname for m in _loaded_modules]
    pymod.environ.set_path(pymod.names.loaded_modules, lm_names)

    lm_files = [m.filename for m in _loaded_modules]
    pymod.environ.set_path(pymod.names.loaded_module_files, lm_files)


def increment_refcount(module):
    module.refcount += 1


def decrement_refcount(module):
    module.refcount -= 1


def register_module(module):
    """Register the `module` to the list of loaded modules"""
    # Update the environment
    if not pymod.modulepath.contains(module.modulepath):
        raise pymod.error.InconsistentModuleStateError(module)
    if (pymod.config.get('skip_add_devpack') and
        module.name.startswith(('sems-devpack', 'devpack'))):
        return
    loaded_modules = get_loaded_modules()
    if module not in loaded_modules:
        increment_refcount(module)
        loaded_modules.append(module)
        set_loaded_modules(loaded_modules)
    else:
        raise ModuleRegisteredError(module)


def unregister_module(module):
    """Unregister the `module` to the list of loaded modules"""
    # Don't use `get_loaded_modules` because the module we are unregistering
    # may no longer be available. `get_loaded_modules` makes some assumptions
    # that can be violated in certain situations. Like, for example, # when
    # "unusing" a directory on the MODULEPATH which has loaded modules.
    # Those modules are automaically unloaded since they are no longer
    # available.
    loaded_modules = get_loaded_modules()
    for (i, loaded) in enumerate(loaded_modules):
        if loaded.filename == module.filename:
            break
    else:
        raise ModuleNotRegisteredError(module)
    module.refcount = 0
    loaded_modules.pop(i)
    set_loaded_modules(loaded_modules)


def swapped_explicitly(old, new):
    _swapped_explicitly.append((old, new))


def swapped_on_version_change(old, new):
    _swapped_on_version_change.append((old, new))


def swapped_on_mp_change(old, new):
    _swapped_on_mp_change.append((old, new))


def unloaded_on_mp_change(old):
    _unloaded_on_mp_change.append(old)


def swapped_on_family_update(old, new):
    _swapped_on_family_update.append((old, new))


def format_changed_module_state():
    sio = StringIO()
    debug_mode = pymod.config.get('debug')

    # Report swapped
    if _swapped_explicitly:
        sio.write('\nThe following modules have been swapped\n')
        for (i, (m1, m2)) in enumerate(_swapped_explicitly):
            a, b = m1.fullname, m2.fullname
            sio.write('  {0}) {1} => {2}\n'.format(i+1, a, b))

    # Report reloaded
    if _swapped_on_family_update:  # pragma: no cover
        sio.write('\nThe following modules in the same family have '
                  'been updated with a version change:\n')
        for (i, (m1, m2)) in enumerate(_swapped_on_family_update):
            a, b, fam = m1.fullname, m2.fullname, m1.family
            sio.write('  {0}) {1} => {2} ({3})\n'.format(i+1, a, b, fam))

    if _swapped_on_version_change:
        sio.write('\nThe following modules have been updated '
                  'with a version change:\n')
        for (i, (m1, m2)) in enumerate(_swapped_on_version_change):
            a, b = m1.fullname, m2.fullname
            sio.write('  {0}) {1} => {2}\n'.format(i+1, a, b))

    # Report changes due to to change in modulepath
    if _unloaded_on_mp_change:  # pragma: no cover
        lm_files = [_.filename for _ in get_loaded_modules()]
        unloaded = [_ for _ in _unloaded_on_mp_change
                    if _.filename not in lm_files]
        sio.write('\nThe following modules have been unloaded '
                  'with a MODULEPATH change:\n')
        for (i, m) in enumerate(unloaded):
            sio.write('  {0}) {1}\n'.format(i+1, m.fullname))

    if _swapped_on_mp_change:
        sio.write('\nThe following modules have been updated '
                  'with a MODULEPATH change:\n')
        for (i, (m1, m2)) in enumerate(_swapped_on_mp_change):
            a, b = m1.fullname, m2.fullname
            if debug_mode:  # pragma: no cover
                n = len('  {0}) '.format(i+1))
                a += ' ({0})'.format(m1.modulepath)
                b = '\n' + ' ' * n + b + ' ({0})'.format(m2.modulepath)
            sio.write('  {0}) {1} => {2}\n'.format(i+1, a, b))

    return sio.getvalue()


class ModuleRegisteredError(Exception):
    def __init__(self, module):
        msg = 'Attempting to register {0} which is already registered!'
        superini = super(ModuleRegisteredError, self).__init__
        superini(msg.format(module))


class ModuleNotRegisteredError(Exception):
    def __init__(self, module):
        msg = 'Attempting to unregister {0} which is not registered!'
        superini = super(ModuleNotRegisteredError, self).__init__
        superini(msg.format(module))
