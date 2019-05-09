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


def swap(mode, name_a, name_b, **kwargs):
    pymod.modes.assert_known_mode(mode)
    if mode != pymod.modes.unload:
        # We don't swap modules in unload mode
        return pymod.mc.swap(name_a, name_b, caller='modulefile')


def load_first(mode, *names):
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


def load(mode, name, **kwds):
    opts = kwds.get('opts', None)
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.unload:
        # We are in unload mode and the module was requested to be loaded.
        # So, we reverse the action and unload it
        pymod.mc.unload(name, caller='modulefile')
    else:
        pymod.mc.load(name, opts=opts, caller='modulefile')


def unload(mode, name):
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
    if mode != pymod.modes.unload:
        return pymod.environ.unset(name)

def set_alias(mode, name, value):
    if mode == pymod.modes.unload:
        pymod.environ.unset_alias(name)
    else:
        pymod.environ.set_alias(name, value)


def unset_alias(mode, name):
    if mode != pymod.modes.unload:
        pymod.environ.unset_alias(name)


def set_shell_function(mode, name, value):
    if mode == pymod.modes.unload:
        pymod.environ.unset_shell_function(name)
    else:
        pymod.environ.set_shell_function(name, value)


def unset_shell_function(mode, name):
    if mode != pymod.modes.unload:
        pymod.environ.unset_shell_function(name)


def prereq_any(mode, *names):
    if mode == pymod.modes.load:
        pymod.mc.prereq_any(*names)


def prereq(mode, *names):
    if mode == pymod.modes.load:
        pymod.mc.prereq(*names)


def conflict(mode, module, *conflicting):
    if mode == pymod.modes.load:
        pymod.mc.conflict(module, *conflicting)


def append_path(mode, name, *values, **kwds):
    """Append `value` to path-like variable `name`"""
    if name == pymod.names.modulepath:
        for value in values:
            use(mode, value, append=True)
        return
    sep = kwds.get('sep', os.pathsep)
    if mode == pymod.modes.unload:
        for value in values:
            pymod.environ.remove_path(name, value, sep)
    else:
        for value in values:
            pymod.environ.append_path(name, value, sep)


def prepend_path(mode, name, *values, **kwds):
    if name == pymod.names.modulepath:
        for value in values:
            use(mode, value)
        return
    sep = kwds.get('sep', os.pathsep)
    if mode == pymod.modes.unload:
        for value in values:
            pymod.environ.remove_path(name, value, sep)
    else:
        for value in values:
            pymod.environ.prepend_path(name, value, sep)


def remove_path(mode, name, *values, **kwds):
    if name == pymod.names.modulepath:
        for value in values:
            unuse(mode, value)
        return
    sep = kwds.get('sep', os.pathsep)
    if mode == pymod.modes.load:
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
