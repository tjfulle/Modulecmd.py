"""Defines callback functions between modules and pymod.

Every function has for the first two arguments: module, mode

"""

from __future__ import print_function

import os
import re

import pymod.modes

from llnl.util.lang import attr_setdefault
import llnl.util.tty as tty


CATEGORY = "category"


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
