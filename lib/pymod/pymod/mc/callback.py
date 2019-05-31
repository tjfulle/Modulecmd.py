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

    Returns
    -------
    Module
       `cur`'s module object

    Notes
    -----
    In load mode, perform an unload of `cur` followed by a load of `new`.
    However, when unloading `cur`, all modules loaded after `cur` are also
    unloaded in reverse order.  After loading `new`, the unloaded modules are
    reloaded in the order they were originally loaded.  If MODULEPATH
    changes as a result of the swap, it is possible that some of these modules
    will be swapped themselves, or not reloaded at all.

    In unload mode, the swap is not performed.

    """
    pymod.modes.assert_known_mode(mode)
    if mode != pymod.modes.unload:
        # We don't swap modules in unload mode
        return pymod.mc.swap(cur, new, caller='modulefile')


def load_first(module, mode, *names):
    """Load the first of modules in `names`

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    names : tuple
        Names of modules to load

    Returns
    -------
    Module
        The loaded module

    Raises
    ------
    ModuleNotFoundError
        If no available modules are found in `names`

    Notes
    -----
    In load mode, loads the first available module in `names` and returns it. In
    unload mode, the first loaded module in `names` is unloaded.

    If the last of `names` is None, no error is thrown if no available
    modules are found in `names`

    """
    pymod.modes.assert_known_mode(mode)
    for name in names:
        if name is None:
            continue
        try:
            if mode == pymod.modes.unload:
                # We are in unload mode and the module was requested to be
                # loaded. So, we reverse the action and unload it
                return pymod.mc.unload(name, caller='load_first')
            else:
                return pymod.mc.load(name, caller='load_first')
        except ModuleNotFoundError:
            continue
    if names and name is None:
        return
    raise ModuleNotFoundError(','.join(names))


def load(module, mode, name, **kwds):
    """Load the module `name`

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    name : str
        Name of the module to load

    Returns
    -------
    Module
        The loaded module

    Raises
    ------
    ModuleNotFoundError
        If no available module is found by `name`

    Notes
    -----
    In load mode, loads the module found by `name` if it is not already loaded.
    If it is loaded, its internal reference count is incremented.

    In unload mode, decrements the reference count of the module found by
    `name`.  If the reference count gets to 0, the module is unloaded.

    """
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
    """Unload the module `name`

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    name : str
        Name of the module to unload

    Returns
    -------
    Module
        The loaded module

    Notes
    -----
    In load mode, decrements the reference count of the module found by `name`.
    If the reference count drops to 0, the module is unloaded.

    If the module is not found, or is not loaded, nothing is done.

    In unload mode, nothing is done.

    """
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
    """Report whether the module `name` is loaded

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    name : str
        Name of the module to report

    Returns
    -------
    bool
        Whether the module given by `name` is loaded

    """
    pymod.modes.assert_known_mode(mode)
    other = pymod.modulepath.get(name)
    if other is None:
        return None
    return other.is_loaded


def use(module, mode, dirname, append=False):
    """Add the directory `dirname` to MODULEPATH

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    dirname : str
        Name of the directory to add to MODULEPATH
    append : bool {False}
        Append `dirname` to MODULEPATH, otherwise `dirname` is preprended

    Notes
    -----
    In load mode, add `dirname` to MODULEPATH.  In unload mode, remove
    `dirname` from MODULEPATH (if it is on MODULEPATH).

    This function potentially has side effects on the environment.  When
    a directory is `use`d, modules in its path may have higher precedence than
    modules on the previous MODULEPATH.  Thus, defaults could change and loaded
    modules could be swapped for newer modules with higher precedence.

    """
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.unload:
        pymod.mc.unuse(dirname)
    else:
        pymod.mc.use(dirname, append=append)
        module.unlocks_dir(dirname)


def unuse(module, mode, dirname):
    """Remove the directory `dirname` from MODULEPATH

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    dirname : str
        Name of the directory to remove from MODULEPATH

    Notes
    -----
    In load mode, removes `dirname` from MODULEPATH (it it is on MODULEPATH).
    In unload mode, nothing is done.

    This function potentially has side effects on the environment.  When
    a directory is `unuse`d, modules in its path will become unavailable and, if
    loaded, will be unloaded.

    """
    pymod.modes.assert_known_mode(mode)
    if mode != pymod.modes.unload:
        pymod.mc.unuse(dirname)


def source(module, mode, filename):
    """Sources a shell script given by filename

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    filename : str
        Name of the filename to source

    Notes
    -----
    Warning: this function sources a shell script unconditionally.  Environment
    modifications made by the script are not tracked by Modulecmd.py.

    `filename` is only sourced in load mode and is only sourced once

    """
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.load:
        pymod.mc.source(filename)


def whatis(module, mode, *args, **kwargs):
    """Sets the "whatis" informational string for `module`

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    args : tuple of str
        Information about the module

    """
    pymod.modes.assert_known_mode(mode)
    return module.set_whatis(*args, **kwargs)


def help(module, mode, help_string, **kwargs):
    """Sets a help message for `module`

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    help_str : str
        Help message for the module

    """
    pymod.modes.assert_known_mode(mode)
    module.set_help_string(help_string)


def setenv(module, mode, name, value):
    """Set value of environment variable `name`

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    name : str
        Name of the environment variable
    value : str
        Value to set for environment variable `name`

    Notes
    -----
    In load mode, sets the environment variable.  In unload mode, unsets the
    variable.

    """
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.unload:
        return pymod.environ.unset(name)
    else:
        return pymod.environ.set(name, value)

def unsetenv(module, mode, name):
    """Unset value of environment variable `name`

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    name : str
        Name of the environment variable

    Notes
    -----
    In unload mode, nothing is done

    """
    pymod.modes.assert_known_mode(mode)
    if mode != pymod.modes.unload:
        return pymod.environ.unset(name)

def set_alias(module, mode, name, value):
    """Define a shell alias

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    name : str
        Name of the alias
    value : str
        Value of the alias

    Notes
    -----
    In load mode, defines the shell alias.  In unload mode, undefines it.

    """
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.unload:
        pymod.environ.unset_alias(name)
    else:
        pymod.environ.set_alias(name, value)


def unset_alias(module, mode, name):
    """Undefine a shell alias

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    name : str
        Name of the alias

    Notes
    -----
    In unload mode, nothing is done.  Otherwise, the alias given by `name` is
    undefined.

    """
    pymod.modes.assert_known_mode(mode)
    if mode != pymod.modes.unload:
        pymod.environ.unset_alias(name)


def set_shell_function(module, mode, name, value):
    """Define a shell function

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    name : str
        Name of the function
    value : str
        Value of the function

    Notes
    -----
    In load mode, defines the shell function.  In unload mode, undefines it.

    """
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.unload:
        pymod.environ.unset_shell_function(name)
    else:
        pymod.environ.set_shell_function(name, value)


def unset_shell_function(module, mode, name):
    """Undefine a shell function

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    name : str
        Name of the function

    Notes
    -----
    In unload mode, nothing is done.  Otherwise, the function given by `name` is
    undefined.

    """
    pymod.modes.assert_known_mode(mode)
    if mode != pymod.modes.unload:
        pymod.environ.unset_shell_function(name)


def prereq_any(module, mode, *names):
    """Defines prerequisites (modules that must be loaded) for this module

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    names : tuple of str
        Names of prerequisite modules

    Notes
    -----
    In load mode, asserts that at least one of the modules given by `names` is
    loaded.  In unload mode, nothing is done.

    FIXME: This function should execute mc.prereq_any in any mode other than
    unload.  In whatis, help, show, etc. modes, it should register the prereqs
    but not enforce them.

    """
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.load:
        pymod.mc.prereq_any(*names)


def prereq(module, mode, *names):
    """Defines a prerequisite (module that must be loaded) for this module

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    name : str
        Name of the prerequisite module

    Notes
    -----
    In load mode, asserts that `name` is loaded.  Otherwise, nothing is done.

    FIXME: This function should execute mc.prereq in any mode other than
    unload.  In whatis, help, show, etc. modes, it should register the prereqs
    but not enforce them.

    """
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.load:
        pymod.mc.prereq(*names)


def conflict(module, mode, *names, **kwargs):
    """Defines conflicts (modules that conflict with `module`)

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    names : tuple of str
        Names of conflicting modules

    Notes
    -----
    In load mode, asserts that none of `names` is loaded.   Otherwise, nothing
    is done.

    FIXME: This function should execute mc.conflict in any mode other than
    unload.  In whatis, help, show, etc. modes, it should register the conflicts
    but not enforce them.

    """
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.load:
        pymod.mc.conflict(module, *names)


def append_path(module, mode, name, *values, **kwds):
    """Append `values` to path-like variable `name`

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    name : str
        Name of path-like variable
    values : tuple of str
        The values to append to path-like variable `name`
    kwds : dict
        kwds['sep'] defines the separator between values in path-like variable
        `name`.  Defaults to os.pathsep

    Notes
    -----
    In unload mode, `values` are removed from path-like variable `name`,
    otherwise, they are appended.

    If `name==MODULEPATH`, this function calls `use(value, append=True)`
    for each `value` in `values`.

    A path-like variable stores a list as a `sep` separated string.  eg, the
    PATH environment variable is a `sep` separated list of directories:

        echo $PATH
        dirname1:dirname2:...

    Here, ":" is the separator `sep`.

    """
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
    """Prepend `values` to path-like variable `name`

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    name : str
        Name of path-like variable
    values : tuple of str
        The values to prepend to path-like variable `name`
    kwds : dict
        kwds['sep'] defines the separator between values in path-like variable
        `name`.  Defaults to os.pathsep

    Notes
    -----
    In unload mode, `values` are removed from path-like variable `name`,
    otherwise, they are prepended.

    If `name==MODULEPATH`, this function calls `use(value)` for each
    `value` in `values`.

    A path-like variable stores a list as a `sep` separated string.  eg, the
    PATH environment variable is a `sep` separated list of directories:

        echo $PATH
        dirname1:dirname2:...

    Here, ":" is the separator `sep`.

    """
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
    """Removes `values` from path-like variable `name`

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    name : str
        Name of path-like variable
    values : tuple of str
        The values to remove from path-like variable `name`
    kwds : dict
        kwds['sep'] defines the separator between values in path-like variable
        `name`.  Defaults to os.pathsep

    Notes
    -----
    In unload mode, nothing is done.  Otherwise, `values` are removed from
    path-like variable `name`.

    If `name==MODULEPATH`, this function calls `unuse(value)` for each
    `value` in `values`.

    A path-like variable stores a list as a `sep` separated string.  eg, the
    PATH environment variable is a `sep` separated list of directories:

        echo $PATH
        dirname1:dirname2:...

    Here, ":" is the separator `sep`.

    """
    pymod.modes.assert_known_mode(mode)
    if name == pymod.names.modulepath:
        for value in values:
            unuse(module, mode, value)
        return
    sep = kwds.get('sep', os.pathsep)
    if mode != pymod.modes.unload:
        for value in values:
            pymod.environ.remove_path(name, value, sep)


def family(module, mode, family_name, **kwargs):
    """Defines the "family" of the module

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    family_name : str
        Name of the family

    Notes
    -----
    Only one module in a family can be loaded at a time.  For instance, GCC and
    Intel compiler modules can define their family as "compiler".  This prevents
    GCC and Intel compilers being loaded simultaneously.

    This function potentially has side effects on the environment.  When
    a module is loaded, if a module of the same family is already loaded, they
    will be swapped.  Swapping has the potential to change the MODULEPATH and
    state of loaded modules.

    """
    pymod.modes.assert_known_mode(mode)
    pymod.mc.family(module, mode, family_name)


def get_family_info(module, mode, name, **kwargs):
    """Returns information about family `name`

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    name : str
        The name of the family to get information about

    Returns
    -------
    str
        The module name in family `name`
    str
        The version of the module in family `name`

    Notes
    -----
    If a module of family `name` is loaded, this function returns its name and
    version.  Otherwise, the name and version return as `None`

    """
    pymod.modes.assert_known_mode(mode)
    name_envar = pymod.names.family_name(name)
    version_envar = pymod.names.family_version(name)
    return pymod.environ.get(name_envar), pymod.environ.get(version_envar)


def execute(module, mode, command, when=None):
    """Executes the command `command` in a subprocess

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    command : str
        The command to execute in a shell subprocess
    when : bool
        Logical describing when to execute `command`.  If `None` or `True`,
        `command` is executed.

    """
    pymod.modes.assert_known_mode(mode)
    if when is not None and not when:
        return
    pymod.mc.execute(command)


