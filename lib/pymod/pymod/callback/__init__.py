"""Defines callback functions between modules and pymod.

Every function has for the first two arguments: module, mode

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


_cb_instructions = []
def log_callback(func_name, *args, **kwargs):
    signature = '{0}('.format(func_name)
    if args:
        signature += ', '.join('{0!r}'.format(_) for _ in args)
    if kwargs:
        if args:
            signature += ', '
        signature += ', '.join('{0}={1!r}'.format(*_) for _ in kwargs.items())
    signature += ')'
    _cb_instructions.append(signature)


def get_current_instructions(reset=False):
    global _cb_instructions
    string = '\n'.join(_cb_instructions)
    if reset:
        _cb_instructions = []
    return string


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
    if when is None:
        when = (mode != pymod.modes.load_partial and
                mode not in pymod.modes.informational)
    if not when:
        func = lambda *args, **kwargs: None
    def wrapper(*args, **kwargs):
        if mode == pymod.modes.show:
            log_callback(func_name, *args, **kwargs)
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
