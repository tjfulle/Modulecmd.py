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
    'get_refcount',
    'set_refcount',
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
]


def module_is_loaded(key):
    if isinstance(key, pymod.module.Module):
        return key in get_loaded_modules()
    elif os.path.isfile(key):
        return key in get_lm_files()
    else:
        for module in get_loaded_modules():
            if module.name == key or module.fullname == key:
                return True
    return False


def get_lm_files():
    return pymod.environ.get_path(pymod.names.loaded_module_files)


def get_lm_names():
    return pymod.environ.get_path(pymod.names.loaded_modules)


def get_loaded_modules():
    global _loaded_modules
    if _loaded_modules is None:
        _loaded_modules = []
        lm_cellar = pymod.environ.get_list(pymod.names.loaded_module_cellar)
        for item in lm_cellar:
            module = pymod.modulepath.get(item['filename'])
            assert module.fullname == item['fullname']
            module.family = item['family']
            module.opts = item['opts']
            module.acquired_as = item['acquired_as']
            _loaded_modules.append(module)
    # return copy so that no one else can modify the loaded modules
    return list(_loaded_modules)


def set_loaded_modules(modules):
    """Set environment variables for loaded module names and files"""
    global _loaded_modules
    _loaded_modules = modules

    assert all([m.acquired_as is not None for m in _loaded_modules])
    lm = [dict(fullname=m.fullname, filename=m.filename,
               family=m.family, opts=m.opts, acquired_as=m.acquired_as)
          for m in _loaded_modules]
    pymod.environ.set_list(pymod.names.loaded_module_cellar, lm)

    # The following are for compatibility with other module programs
    lm_names = [m.fullname for m in _loaded_modules]
    pymod.environ.set_path(pymod.names.loaded_modules, lm_names)

    lm_files = [m.filename for m in _loaded_modules]
    pymod.environ.set_path(pymod.names.loaded_module_files, lm_files)


def get_lm_refcount():
    return pymod.environ.get_dict(pymod.names.loaded_module_refcount)


def set_lm_refcount(lm_refcount):
    pymod.environ.set_dict(pymod.names.loaded_module_refcount, lm_refcount)


def get_refcount(module=None):
    refcount = get_lm_refcount()
    if module is None:
        return refcount
    return refcount.get(module.fullname, 0)


def pop_refcount(module):
    lm_refcount = get_lm_refcount()
    lm_refcount.pop(module.fullname, None)
    set_lm_refcount(lm_refcount)


def set_refcount(module, count):  # pragma: no cover
    name = module.fullname
    lm_refcount = get_lm_refcount()
    lm_refcount[name] = count
    if not lm_refcount[name]:
        lm_refcount.pop(name)
    set_lm_refcount(lm_refcount)


def increment_refcount(module):
    name = module.fullname
    lm_refcount = get_lm_refcount()
    lm_refcount[name] = lm_refcount.pop(name, 0) + 1
    set_lm_refcount(lm_refcount)


def decrement_refcount(module, count=None):
    name = module.fullname
    lm_refcount = get_lm_refcount()
    lm_refcount[name] = lm_refcount.pop(name, 1) - 1
    if not lm_refcount[name]:
        lm_refcount.pop(name)
    set_lm_refcount(lm_refcount)


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
        loaded_modules.append(module)
        set_loaded_modules(loaded_modules)
        increment_refcount(module)
    elif pymod.config.get('debug'):  # pragma: no cover
        tty.die('Attempting to register {0} which is already loaded!'
                .format(module))


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
    else:  # pragma: no cover
        tty.die('Attempting to unregister {0} which is not loaded!'
                .format(module))
    loaded_modules.pop(i)
    set_loaded_modules(loaded_modules)
    pop_refcount(module)


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
        lm_files = get_lm_files()
        unloaded = [m for m in _unloaded_on_mp_change
                    if m.filename not in lm_files]
        sio.write('\nThe following modules have been unloaded '
                  'with a MODULEPATH change:\n')
        for (i, m) in enumerate(unloaded):
            sio.write('  {0}) {1}\n'.format(i+1, m.fullname))

    if _swapped_on_mp_change:
        sio.write('\nThe following modules have been updated '
                  'with a MODULEPATH change:\n')
        for (i, (m1, m2)) in enumerate(_swapped_on_mp_change):
            a, b = m1.fullname, m2.fullname
            sio.write('  {0}) {1} => {2}\n'.format(i+1, a, b))

    return sio.getvalue()
