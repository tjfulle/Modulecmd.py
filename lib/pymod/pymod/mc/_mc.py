import os
from six import StringIO

import pymod.names
import pymod.error
import pymod.environ
import pymod.modulepath

import contrib.util.misc as misc
import contrib.util.logging as logging

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
    'pop_refcount',
    'increment_refcount',
    'decrement_refcount',
    'swapped_explicitly',
    'swapped_on_version_change',
    'swapped_on_family_update',
    'swapped_on_mp_change',
    'unloaded_on_mp_change',
    'on_module_load',
    'on_module_unload',
]


def get_loaded_modules():
    lm_files = loaded_module_files()
    lm_opts = pymod.environ.get_dict(pymod.names.loaded_module_opts)
    loaded_modules = [pymod.modulepath.get(f) for f in lm_files]
    for module in loaded_modules:
        m_opts = lm_opts.get(module.fullname)
        if m_opts and not module.opts:
            module.opts = m_opts
    return loaded_modules


def set_loaded_modules(modules):
    """Set environment variables for loaded module names and files"""
    lm_names = [m.fullname for m in modules]
    pymod.environ.set_path(pymod.names.loaded_modules, lm_names)

    lm_files = [m.filename for m in modules]
    pymod.environ.set_path(pymod.names.loaded_module_files, lm_files)

    lm_opts = dict([(m.fullname, m.opts) for m in modules if m.opts])
    pymod.environ.set_dict(pymod.names.loaded_module_opts, lm_opts)


def loaded_module_files():
    return pymod.environ.get_path(pymod.names.loaded_module_files)


def loaded_module_names():
    return pymod.environ.get_path(pymod.names.loaded_modules)


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


def set_refcount(module, count):
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


def on_module_load(module, do_not_register=False):
    """Register the `module` to the list of loaded modules"""
    # Update the environment
    if not pymod.modulepath.contains(module.modulepath):
        raise pymod.error.InconsistentModuleStateError(module)
    if (pymod.config.get('skip_add_devpack') and
        module.name.startswith('devpack')):
        return
    if do_not_register or module.do_not_register:
        return
    loaded_modules = get_loaded_modules()
    if module not in loaded_modules:
        loaded_modules.append(module)
        set_loaded_modules(loaded_modules)


def on_module_unload(module):
    """Unregister the `module` to the list of loaded modules"""
    # Update the environment
    # Make sure this module is removed
    loaded_modules = get_loaded_modules()
    if module in loaded_modules:
        i = loaded_modules.index(module)
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

    # Report swapped
    if _swapped_explicitly:
        sio.write('\nThe following modules have been swapped\n')
        for (i, (m1, m2)) in enumerate(_swapped_explicitly):
            a, b = m1.fullname, m2.fullname
            sio.write('  {0}) {1} => {2}\n'.format(i+1, a, b))

    # Report reloaded
    if _swapped_on_family_update:
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
    if _unloaded_on_mp_change:
        lm_files = loaded_module_files()
        unloaded = [m for m in _unloaded_on_mp_change
                    if m.filename not in lm_files]
        sio.write('\nThe following modules have been unloaded '
                  'with a MODULEPATH change:\n')
        for (i, m) in enumerate(unloaded):
            sio.write('  {0}) {1}\n'.format(i+1, m.fullname))

    if _swapped_on_mp_change:
        sio.write('\nThe following modules have been updated '
                  'with a MODULEPATH change:\n')
        for (i, (m1, m2)) in enumerate(swapped):
            a, b = m1.fullname, m2.fullname
            sio.write('  {0}) {1} => {2}\n'.format(i+1, a, b))

    return sio.getvalue()
