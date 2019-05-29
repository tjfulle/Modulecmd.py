import os

import pymod.mc
import pymod.modes
import pymod.modulepath
from pymod.error import ModuleNotFoundError

"""Defines callback functions between modules and pymod.

Every function has for the first two arguments: module, mode


"""

__all__ = ['callback']


def callback(func, module, mode, when=None, **kwds):
    """Create a callback function by wrapping `func`

    Parameters
    ----------
    func : function
        The function object to wrap
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    when : bool
        Conditional defining when to evaluate the callback.  If None (unset) or
        True, the function `func` is wrapped.  Otherwise, an empty lambda is
        wrapped.
    kwds : dict
        Extra keyword arguments to be sent to `func`

    Notes
    -----
    This function is intended to be used by pymod.mc.execmodule to wrap
    functions to be sent to modules being executed.  The functions allow modules
    to interact with and modify pymod.environ, which in turn modifies the
    user's shell environment.

    The `module` and `mode` arguments are the first two arguments to any
    function wrapped.  `module` is the Module object of the module being
    executed and `mode` is the execution mode (i.e., 'load', 'unload', etc.)

    """
    if when is None:
        when = (mode != pymod.modes.load_partial and
                mode not in pymod.modes.informational)
    if not when:
        func = lambda *args, **kwargs: None
    def wrapper(*args, **kwargs):
        kwargs.update(kwds)
        return func(module, mode, *args, **kwargs)
    return wrapper


def swap(module, mode, cur, new, **kwargs):
    """Swap module `cur` for module `new`

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    cur : str
        The name of the module to unload
    new : str
        The name of the module to load in place of `cur`

    Notes
    -----
    `swap` essentially performs an unload of `cur` followed by a load of `new`.
    However, when unloading `cur`, all modules loaded after `cur` are also
    unloaded in reverse order.  After loading `new`, the unloaded modules are
    reloaded in the order they were originally loaded.  If the MODULEPATH
    changes as a result of the swap, it is possible that some of these modules
    will be swapped themselves, or not reloaded at all.

    The swap is not performed if `mode` == 'unload'.

    """
    pymod.modes.assert_known_mode(mode)
    if mode != pymod.modes.unload:
        # We don't swap modules in unload mode
        return pymod.mc.swap(cur, new, caller='modulefile')


def load_first(module, mode, *names):
    pymod.modes.assert_known_mode(mode)
    for name in names:
        if name is None:
            continue
        try:
            if mode == pymod.modes.unload:
                # We are in unload mode and the module was requested to be
                # loaded. So, we reverse the action and unload it
                return pymod.mc.unload(name, caller='load_first')
            elif mode == pymod.modes.load:
                return pymod.mc.load(name, caller='load_first')
        except ModuleNotFoundError:
            continue
    if name is None:
        return
    raise ModuleNotFoundError(','.join(names))


def load(module, mode, name, **kwds):
    pymod.modes.assert_known_mode(mode)
    opts = kwds.get('opts', None)
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.unload:
        # We are in unload mode and the module was requested to be loaded.
        # So, we reverse the action and unload it
        try:
            pymod.mc.unload(name, caller='modulefile')
        except ModuleNotFoundError:
            return
    else:
        pymod.mc.load(name, opts=opts, caller='modulefile')


def unload(module, mode, name):
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


def is_loaded(module, mode, name):
    pymod.modes.assert_known_mode(mode)
    other = pymod.modulepath.get(name)
    if other is None:
        return None
    return other.is_loaded


def use(module, mode, dirname, append=False):
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.unload:
        pymod.mc.unuse(dirname)
    else:
        pymod.mc.use(dirname, append=append)
        module.unlocks_dir(dirname)


def unuse(module, mode, dirname):
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.load:
        pymod.mc.unuse(dirname)


def source(module, mode, filename):
    """Source a script"""
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.load:
        pymod.mc.source(filename)


def whatis(module, mode, *args, **kwargs):
    pymod.modes.assert_known_mode(mode)
    return module.set_whatis(*args, **kwargs)


def help(module, mode, help_string, **kwargs):
    pymod.modes.assert_known_mode(mode)
    module.set_help_string(help_string)


def setenv(module, mode, name, value):
    """Set value of environment variable `name`"""
    pymod.modes.assert_known_mode(mode)
    if mode in (pymod.modes.load,):
        return pymod.environ.set(name, value)
    elif mode in (pymod.modes.unload,):
        return pymod.environ.unset(name)

def unsetenv(module, mode, name):
    """Set value of environment variable `name`"""
    pymod.modes.assert_known_mode(mode)
    if mode != pymod.modes.unload:
        return pymod.environ.unset(name)

def set_alias(module, mode, name, value):
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.unload:
        pymod.environ.unset_alias(name)
    else:
        pymod.environ.set_alias(name, value)


def unset_alias(module, mode, name):
    pymod.modes.assert_known_mode(mode)
    if mode != pymod.modes.unload:
        pymod.environ.unset_alias(name)


def set_shell_function(module, mode, name, value):
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.unload:
        pymod.environ.unset_shell_function(name)
    else:
        pymod.environ.set_shell_function(name, value)


def unset_shell_function(module, mode, name):
    pymod.modes.assert_known_mode(mode)
    if mode != pymod.modes.unload:
        pymod.environ.unset_shell_function(name)


def prereq_any(module, mode, *names):
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.load:
        pymod.mc.prereq_any(*names)


def prereq(module, mode, *names):
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.load:
        pymod.mc.prereq(*names)


def conflict(module, mode, *conflicting, **kwargs):
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.load:
        pymod.mc.conflict(module, *conflicting)


def append_path(module, mode, name, *values, **kwds):
    """Append `value` to path-like variable `name`"""
    pymod.modes.assert_known_mode(mode)
    if name == pymod.names.modulepath:
        for value in values:
            use(module, mode, value, append=True)
        return
    sep = kwds.get('sep', os.pathsep)
    if mode == pymod.modes.unload:
        for value in values:
            pymod.environ.remove_path(name, value, sep)
    else:
        for value in values:
            pymod.environ.append_path(name, value, sep)


def prepend_path(module, mode, name, *values, **kwds):
    pymod.modes.assert_known_mode(mode)
    if name == pymod.names.modulepath:
        for value in values:
            use(module, mode, value)
        return
    sep = kwds.get('sep', os.pathsep)
    if mode == pymod.modes.unload:
        for value in values:
            pymod.environ.remove_path(name, value, sep)
    else:
        for value in values:
            pymod.environ.prepend_path(name, value, sep)


def remove_path(module, mode, name, *values, **kwds):
    pymod.modes.assert_known_mode(mode)
    if name == pymod.names.modulepath:
        for value in values:
            unuse(module, mode, value)
        return
    sep = kwds.get('sep', os.pathsep)
    if mode == pymod.modes.load:
        for value in values:
            pymod.environ.remove_path(name, value, sep)


def family(module, mode, family_name, **kwargs):
    """Assign a family"""
    pymod.modes.assert_known_mode(mode)
    pymod.mc.family(module, mode, family_name)


def execute(module, mode, command, when=None):
    pymod.modes.assert_known_mode(mode)
    if when is not None and not when:
        return
    pymod.mc.execute(command)


def get_family_info(module, mode, name, **kwargs):
    pymod.modes.assert_known_mode(mode)
    name_envar = pymod.names.family_name(name)
    version_envar = pymod.names.family_version(name)
    return pymod.environ.get(name_envar), pymod.environ.get(version_envar)
