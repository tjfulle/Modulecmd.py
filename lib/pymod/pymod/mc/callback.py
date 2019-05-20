import os

import pymod.mc
import pymod.modes
import pymod.modulepath
from pymod.error import ModuleNotFoundError

"""Module defines callback functions between modules and pymod.

Every function has for the first two arguments: mode, module


"""

__all__ = ['callback']


def callback(func, mode, module, when=None, **kwds):
    if when is None:
        when = (mode != pymod.modes.load_partial and
                mode not in pymod.modes.informational)
    if not when:
        func = lambda *args, **kwargs: None
    def wrapper(*args, **kwargs):
        kwargs.update(kwds)
        return func(mode, module, *args, **kwargs)
    return wrapper


def swap(mode, module, name_a, name_b, **kwargs):
    pymod.modes.assert_known_mode(mode)
    if mode != pymod.modes.unload:
        # We don't swap modules in unload mode
        return pymod.mc.swap(name_a, name_b, caller='modulefile')


def load_first(mode, module, *names):
    pymod.modes.assert_known_mode(mode)
    for name in names:
        if name is None:
            continue
        try:
            if mode == pymod.modes.unload:
                # We are in unload mode and the module was requested to be
                # loaded. So, we reverse the action and unload it
                return pymod.mc.unload(name, caller='modulefile')
            elif mode == pymod.modes.load:
                return pymod.mc.load(name, caller='modulefile')
        except ModuleNotFoundError:
            continue
    if name is None:
        return
    raise ModuleNotFoundError(','.join(names))


def load(mode, module, name, **kwds):
    pymod.modes.assert_known_mode(mode)
    opts = kwds.get('opts', None)
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.unload:
        # We are in unload mode and the module was requested to be loaded.
        # So, we reverse the action and unload it
        pymod.mc.unload(name, caller='modulefile')
    else:
        pymod.mc.load(name, opts=opts, caller='modulefile')


def unload(mode, module, name):
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.unload:
        # We are in unload mode and the module was requested to be
        # unloaded. But, we don't know if it was previously loaded. So we
        # skip
        return
    else:
        try:
            pymod.mc.unload(name, caller='modulefile')
        except ModuleNotFoundError:
            return None


def is_loaded(mode, module, name):
    pymod.modes.assert_known_mode(mode)
    other = pymod.modulepath.get(name)
    if other is None:
        return None
    return other.is_loaded


def use(mode, module, dirname, append=False):
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.unload:
        pymod.mc.unuse(dirname)
    else:
        pymod.mc.use(dirname, append=append)
        module.unlocks_dir(dirname)


def unuse(mode, module, dirname):
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.load:
        pymod.mc.unuse(dirname)


def source(mode, module, filename):
    """Source a script"""
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.load:
        pymod.mc.source(filename)


def whatis(mode, module, *args, **kwargs):
    pymod.modes.assert_known_mode(mode)
    return module.set_whatis(*args, **kwargs)


def help(mode, module, help_string, **kwargs):
    pymod.modes.assert_known_mode(mode)
    module.set_help_string(help_string)


def setenv(mode, module, name, value):
    """Set value of environment variable `name`"""
    pymod.modes.assert_known_mode(mode)
    if mode in (pymod.modes.load,):
        return pymod.environ.set(name, value)
    elif mode in (pymod.modes.unload,):
        return pymod.environ.unset(name)

def unsetenv(mode, module, name):
    """Set value of environment variable `name`"""
    pymod.modes.assert_known_mode(mode)
    if mode != pymod.modes.unload:
        return pymod.environ.unset(name)

def set_alias(mode, module, name, value):
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.unload:
        pymod.environ.unset_alias(name)
    else:
        pymod.environ.set_alias(name, value)


def unset_alias(mode, module, name):
    pymod.modes.assert_known_mode(mode)
    if mode != pymod.modes.unload:
        pymod.environ.unset_alias(name)


def set_shell_function(mode, module, name, value):
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.unload:
        pymod.environ.unset_shell_function(name)
    else:
        pymod.environ.set_shell_function(name, value)


def unset_shell_function(mode, module, name):
    pymod.modes.assert_known_mode(mode)
    if mode != pymod.modes.unload:
        pymod.environ.unset_shell_function(name)


def prereq_any(mode, module, *names):
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.load:
        pymod.mc.prereq_any(*names)


def prereq(mode, module, *names):
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.load:
        pymod.mc.prereq(*names)


def conflict(mode, module, *conflicting, **kwargs):
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.load:
        pymod.mc.conflict(module, *conflicting)


def append_path(mode, module, name, *values, **kwds):
    """Append `value` to path-like variable `name`"""
    pymod.modes.assert_known_mode(mode)
    if name == pymod.names.modulepath:
        for value in values:
            use(mode, module, value, append=True)
        return
    sep = kwds.get('sep', os.pathsep)
    if mode == pymod.modes.unload:
        for value in values:
            pymod.environ.remove_path(name, value, sep)
    else:
        for value in values:
            pymod.environ.append_path(name, value, sep)


def prepend_path(mode, module, name, *values, **kwds):
    pymod.modes.assert_known_mode(mode)
    if name == pymod.names.modulepath:
        for value in values:
            use(mode, module, value)
        return
    sep = kwds.get('sep', os.pathsep)
    if mode == pymod.modes.unload:
        for value in values:
            pymod.environ.remove_path(name, value, sep)
    else:
        for value in values:
            pymod.environ.prepend_path(name, value, sep)


def remove_path(mode, module, name, *values, **kwds):
    pymod.modes.assert_known_mode(mode)
    if name == pymod.names.modulepath:
        for value in values:
            unuse(mode, module, value)
        return
    sep = kwds.get('sep', os.pathsep)
    if mode == pymod.modes.load:
        for value in values:
            pymod.environ.remove_path(name, value, sep)


def family(mode, module, family_name, **kwargs):
    """Assign a family"""
    pymod.modes.assert_known_mode(mode)
    pymod.mc.family(mode, module, family_name)


def execute(arg_mode, module, command, mode=None):
    pymod.modes.assert_known_mode(arg_mode)
    if mode is not None and mode != pymod.modes.as_string(arg_mode):
        return
    pymod.mc.execute(command)
