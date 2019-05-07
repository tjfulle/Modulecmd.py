import os
import sys

import pymod.mc
import pymod.modes
import pymod.modulepath
from contrib.util import split
from pymod.error import ModuleNotFoundError

import llnl.util.tty as tty

"""Module defines callback functions between modules and pymod"""

__all__ = ['callback']


def callback(func_name, mode, module=None, when=True, memo={}):
    if not when:
        return lambda *args, **kwargs: None
    try:
        module_fun = memo[func_name]
    except KeyError:
        module_fun = getattr(sys.modules[__name__], func_name, None)
        if module_fun is None:
            tty.warn('Callback function {} not defined'
                         .format(func_name))
            module_fun = lambda *args, **kwargs: None
        memo[func_name] = module_fun
    if module is not None:
        def func(*args, **kwargs):
            return module_fun(mode, module, *args, **kwargs)
    else:
        def func(*args, **kwargs):
            return module_fun(mode, *args, **kwargs)
    return func


def swap(mode, m1, m2, **kwargs):
    pymod.modes.assert_known_mode(mode)
    if mode in (pymod.modes.load_partial, pymod.modes.unload):
        # We don't swap modules in unload mode
        return
    module_a = pymod.modulepath.get(m1)
    module_b = pymod.modulepath.get(m2)
    if module_a is None:
        raise ModuleNotFoundError(m1)
    if module_b is None:
        raise ModuleNotFoundError(m2)
    if module_b.is_loaded:
        return
    if not module_a.is_loaded:
        pymod.mc.execmodule(module_b, pymod.modes.load)
        return
    assert module_a.is_loaded
    pymod.mc.swap_impl(module_a, module_b)


def load_first(mode, *names):
    pymod.modes.assert_known_mode(mode)
    if mode in (pymod.modes.unload, pymod.modes.load_partial):
        return None
    for name in names:
        if name is None:
            continue
        module = pymod.modulepath.get(name)
        if module is not None:
            break
    else:
        if name is None:
            # Passes modulename = None as last argument says to ignore
            # if this module is not found
            return None
        raise ModuleNotFoundError(','.join(names))

    if mode == pymod.modes.unload:
        # We are in unload mode and the module was requested to be loaded.
        # So, we reverse the action and unload it
        return pymod.mc.unload_impl(module)
    elif mode == pymod.modes.load:
        return pymod.mc.load_impl(module, increment_refcnt_if_loaded=True)


def load(mode, name, opts=None):
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.load_partial:
        return None
    elif mode == pymod.modes.unload:
        # We are in unload mode and the module was requested to be loaded.
        # So, we reverse the action and unload it
        return pymod.mc.unload(name)
    else:
        return pymod.mc.load(name, opts=opts,
                             increment_refcnt_if_loaded=True)


def unload(mode, name):
    pymod.modes.assert_known_mode(mode)
    if mode in (pymod.modes.unload, pymod.modes.load_partial):
        # We are in unload mode and the module was requested to be
        # unloaded. But, we don't know if it was previously loaded. So we
        # skip
        return None
    else:
        module = pymod.modulepath.get(name)
        if module is None:
            return None
        refcnt = pymod.mc.get_refcount(module)
        if refcnt > 1:
            # Don't unload, just decrement the reference count
            pymod.mc.decrement_refcount(module)
            return

        pymod.mc.unload_impl(module)
        return None


def is_loaded(mode, module):
    return module.is_loaded


def use(mode, dirname, append=False):
    if mode in (pymod.modes.load,):
        pymod.mc.use(dirname, append=append)
    elif mode in (pymod.modes.unload,):
        pymod.mc.unuse(dirname)


def unuse(mode, dirname):
    if mode in (pymod.modes.load,):
        pymod.mc.unuse(value)


def source(mode, filename):
    """Source a script"""
    sourced = pymod.environ.get_path(pymod.names.sourced_files)
    if mode == pymod.modes.load and filename not in sourced:
        if not os.path.isfile(filename):
            tty.die('{0}: no such file to source'.format(filename))
        command = pymod.shell.source_command(filename)
        sourced.append(filename)
        pymod.environ.set_path(pymod.names.sourced_files, sourced)
        sys.stdout.write(command + ';\n')


def whatis(mode, module, *args, **kwargs):
    return module.set_whatis(*args, **kwargs)


def help(mode, module, help_string):
    module.set_help_string(help_string)


def setenv(mode, name, value):
    """Set value of environment variable `name`"""
    if mode in (pymod.modes.load,):
        return pymod.environ.set(name, value)
    elif mode in (pymod.modes.unload,):
        return pymod.environ.unset(name)

def unsetenv(mode, name):
    """Set value of environment variable `name`"""
    if mode in (pymod.modes.load,):
        return pymod.environ.unset(name)

def set_alias(mode, name, value):
    if mode in (pymod.modes.load, pymod.modes.load_partial):
        pymod.environ.set_alias(name, value)
    elif mode in (pymod.modes.unload,):
        pymod.environ.unset_alias(name)


def unset_alias(mode, name):
    if mode in (pymod.modes.load, pymod.modes.load_partial):
        pymod.environ.unset_alias(name)


def set_shell_function(mode, name, value):
    if mode in (pymod.modes.load, pymod.modes.load_partial):
        pymod.environ.set_shell_function(name, value)
    elif mode in (pymod.modes.unload,):
        pymod.environ.unset_shell_function(name)


def unset_shell_function(mode, name):
    if mode in (pymod.modes.load, pymod.modes.load_partial):
        pymod.environ.unset_shell_function(name)


def prereq_any(mode, *names):
    if mode in (pymod.modes.load,):
        pymod.mc.prereq_any(*names)


def prereq(mode, *names):
    if mode in (pymod.modes.load,):
        pymod.mc.prereq(*modulenames)


def conflict(mode, module, *names):
    if mode in (pymod.modes.load,):
        pymod.mc.conflict(module.name, *names)


def append_path(mode, name, *values, **kwds):
    """Append `value` to path-like variable `name`"""
    if name == pymod.names.modulepath:
        for value in values:
            use(mode, value, append=True)
        return
    sep = kwds.get('sep', os.pathsep)
    if mode in (pymod.modes.load,):
        for value in values:
            pymod.environ.append_path(name, value, sep)
    elif mode in (pymod.modes.unload,):
        for value in values:
            pymod.environ.remove_path(name, value, sep)


def prepend_path(mode, name, *values, **kwds):
    if name == pymod.names.modulepath:
        for value in values:
            use(mode, value)
        return
    sep = kwds.get('sep', os.pathsep)
    if mode in (pymod.modes.load,):
        for value in values:
            pymod.environ.prepend_path(name, value, sep)
    elif mode in (pymod.modes.unload,):
        for value in values:
            pymod.environ.remove_path(name, value, sep)


def remove_path(mode, name, *values, **kwds):
    if name == pymod.names.modulepath:
        for value in values:
            unuse(mode, value)
        return
    sep = kwds.get('sep', os.pathsep)
    if mode in (pymod.modes.load,):
        for value in values:
            pymod.environ.remove_path(name, value, sep)


def family(mode, module, family_name):
    """Assign a family"""
    pymod.mc.family(mode, module, family_name)


def execute(mode_, command, mode=None):
    if mode is not None and mode != mode_:
        return
    xc = split(command, ' ', 1)
    exe = Executable(xc[0])
    with open(os.devnull, 'a') as fh:
        kwargs = {
            'env': pymod.environ.filter(),
            'output': fh,
            'error': subprocess.sys.stdout,
        }
        try:
            exe(*xc[1:], **kwargs)
        except:
            tty.warn('Command {0!r} failed'.format(command))
    return
