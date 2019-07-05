"""Defines callback functions between modules and pymod.

Modulecmd.py executes modulefiles in a sandbox with several functions made
available that allow the modulefile to interact with the user's environment.
Each of these functions is defined in this `pymod.callback` package.  The module
`pymod.mc.execmodule` reads in each callback function and sets up a sandbox in
which modulefiles are executed.  Adding a module to this directory, with
a function having the same name as the module, automatically makes that function
available to modulefiles.

Each function is wrapped by the function `callback`, defined below.  It is this
wrapped function that is sent to user's modulefiles.  Each callback function
must have for the first two arguments: module, mode.  The callback wrapper
strips these arguments so that they are *invisible* to user's modulefiles.  Eg,
consider the function `baz` that takes arguments `spam` and `eggs`.  Its
signature is

```
def baz(module, mode, spam, eggs):
    ...
```

But, the wrapped function seen by modulefiles is

```
baz(spam, eggs)
```

This allows the function `baz` to change its implementation depending on the
mode or module.  For instance, when a module is loaded, the function
`append_path(name, path)` appends `path` to the environment variable `name`.
But, when a module is unloaded, `append_path` *removes* `path` from the
environment variable `name`.



"""

from __future__ import print_function

import os
import re
import sys

import pymod.modes
import pymod.paths

from llnl.util.lang import attr_setdefault
import llnl.util.tty as tty


# Patterns to ignore in the callbacks directory when looking for callbacks.
ignore_files = r'^\.|^__init__.py$|^#|flycheck_'

CATEGORY = "category"


#: global, cached list of all callbacks -- access through all_callbacks()
_all_callbacks = None


def log_callback(func_name, *args, **kwargs):
    signature = '{0}('.format(func_name)
    if args:
        signature += ', '.join('{0!r}'.format(_) for _ in args)
    if kwargs:
        if args:
            signature += ', '
        signature += ', '.join('{0}={1!r}'.format(*_) for _ in kwargs.items())
    signature += ')'
    pymod.mc.cur_module_command_his.write(signature + '\n')


def all_callbacks():
    """Get a sorted list of all pymod callbacks.

    This will list the lib/pymod/pymod/callback directory and find the
    callbacks there to construct the list.  It does not actually import
    the python files -- just gets the names.
    """
    global _all_callbacks
    if _all_callbacks is None:
        _all_callbacks = []
        callback_paths = [pymod.paths.callback_path]  # Built-in callbacks
        for path in callback_paths:
            for file in os.listdir(path):
                if file.endswith(".py") and not re.search(ignore_files, file):
                    callback = re.sub(r'.py$', '', file)
                    _all_callbacks.append(callback)

        _all_callbacks.sort()

    return _all_callbacks


def callback(func_name, module, mode, when=None, **kwds):
    """Create a callback function by wrapping `func`

    Parameters
    ----------
    func_name : str
        The name of the function object to wrap
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
    func = get_callback(func_name)
    return callback_impl(func, module, mode, when=when, **kwds)


def callback_impl(func, module, mode, when=None, **kwds):
    if when is None:
        when = (mode != pymod.modes.load_partial and
                mode not in pymod.modes.informational)
    if not when:
        func = lambda *args, **kwargs: None
    def wrapper(*args, **kwargs):
        if mode == pymod.modes.show:
            log_callback(func.__name__, *args, **kwargs)
            if not getattr(func, 'eval_on_show', False):
                return
        kwargs.update(kwds)
        return func(module, mode, *args, **kwargs)
    return wrapper


def get_module(cb_name):
    """Imports the module for a particular callback name and returns it.

    Parameters
    ----------
    cb_name : str
        name of the callback for which to get a module (contains ``-``, not ``_``).
    """
    # Import the callback from the built-in directory
    module_name = '{0}.{1}'.format(__name__, cb_name)
    module = __import__(module_name,
                        fromlist=[cb_name, CATEGORY],
                        level=0)
    tty.debug('Imported {0} from built-in callbacks'.format(cb_name))

    attr_setdefault(module, CATEGORY, "")

    if not hasattr(module, cb_name):  # pragma: no cover
        tty.die("callback module {0} ({1}) must define function {2!r}."
                .format(module.__name__, module.__file__, cb_name))

    return module


def get_callback(cb_name):
    """Imports the callback's function from a module and returns it.

    Parameters
    ----------
    cb_name : str
        name of the callback for which to get a module
    """
    return getattr(get_module(cb_name), cb_name)
