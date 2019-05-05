import os

import pymod.names
import pymod.error
import pymod.environ
import pymod.modulepath

import contrib.util.misc as misc
import contrib.util.logging as logging

_changed_versions = []
_changed_family = []

__all__ = [
    'loaded_modules',
    'loaded_module_files',
    'loaded_module_names',
    'set_loaded_module_files',
    'set_loaded_module_names',
    'set_refcount',
    'pop_refcount',
    'increment_refcount',
    'decrement_refcount',
    'register_changed_version',
    'changed_versions'
]


def loaded_modules():
    return [pymod.modulepath.get(f) for f in loaded_module_files()]


def loaded_module_files():
    return pymod.environ.get_path(pymod.names.loaded_module_files)


def loaded_module_names():
    return pymod.environ.get_path(pymod.names.loaded_modules)


def set_loaded_module_files(lm_files):
    string = join(lm_files, os.pathsep)
    pymod.environ.set(pymod.names.loaded_module_files, string)


def set_loaded_module_names(lm_names):
    string = join(lm_names, os.pathsep)
    pymod.environ.set(pymod.names.loaded_modules, string)


def get_lm_refcount():
    string = pymod.environ.get(pymod.names.loaded_modules_refcount)
    return misc.str2dict(string)


def set_lm_refcount(lm_refcount):
    string = misc.dict2str(lm_refcount)
    pymod.environ.set(pymod.names.loaded_modules_refcount, string)


def pop_refcount(name):
    lm_refcount = get_lm_refcount()
    lm_refcount.pop(name, None)
    set_lm_refcount(lm_refcount)


def set_refcount(name, count):
    lm_refcount = get_lm_refcount()
    lm_refcount[name] = count
    if not lm_refcount[name]:
        lm_refcount.pop(name)
    set_lm_refcount(lm_refcount)


def increment_refcount(name):
    lm_refcount = get_lm_refcount()
    lm_refcount[name] = lm_refcount.pop(name, 0) + 1
    set_lm_refcount(lm_refcount)


def decrement_refcount(name, count=None):
    lm_refcount = get_lm_refcount()
    lm_refcount[name] = lm_refcount.pop(name, 1) - 1
    if not lm_refcount[name]:
        lm_refcount.pop(name)
    set_lm_refcount(lm_refcount)


def register_changed_version(old, new):
    _changed_versions.append((old.fullname, new.fullname))


def changed_versions():
    for (old, new) in _changed_versions:
        yield (old, new)


def register_changed_family(old, new):
    _changed_family.append((old.family, old.fullname, new.fullname))


def changed_families():
    for (family, old, new) in _changed_versions:
        yield (family, old, new)


def on_module_load(module, do_not_register=False):
    """Register the `module` to the list of loaded modules"""
    # Update the environment
    if pymod.modulepath.contains(module.modulepath):
        raise pymod.errors.InconsistentModuleState(module)
    if pymod.config.get('skip_add_devpack') and module.name.startswith('devpack'):
        return
    if do_not_register or module.do_not_register:
        return
    if not module.is_loaded:
        add_module_to_env(module)
    if module.fullname not in pymod.environ.get_loaded_modules('names'):
        msg = 'Expected to find {0} in LOADEDMODULES'.format(module)
        logging.error(msg)


def add_module_to_env(self, module):
    assert not module.is_loaded, 'Module should not be loaded now'
    lm_names = pymod.mc.loaded_module_names()
    lm_files = pymod.mc.loaded_module_files()
    if module.fullname not in lm_names:
        if module.filename in lm_files:
            raise Exception('Path for {0} SHOULD NOT be in _LMFILES_ '
                            'at this point (1)!'.format(module))
        lm_names.append(module.fullname)
        set_loaded_module_names(lm_names)
        lm_files.append(module.filename)
        set_loaded_module_files(lm_files)
    elif module.filename not in lm_files:
        raise Exception('Path for {0} SHOULD be in _LMFILES_ '
                        'at this point (2)!'.format(module))
    lm_opts = loaded_module_opts()
    if module.fullname not in lm_opts:
        opts = module.get_set_options()
        lm_opts[module.fullname] = opts
        set_loaded_module_opts(lm_opts)
    module.is_loaded = True


def on_module_unload(self, module):
    """Unregister the `module` to the list of loaded modules"""
    # Update the environment
    # Make sure this module is removed
    if module.is_loaded:
        self.remove_module_from_env(module)
    loaded = loaded_module_names()
    if loaded and module.fullname in loaded:
        raise Exception('{0} module still in {1}!'
                        .format(module, pymod.names.loaded_modules))
