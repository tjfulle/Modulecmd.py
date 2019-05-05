import sys
import socket
import subprocess

import pymod.environ
from contrib.util.logging.color import colorize
import contrib.util.logging as logging
import contrib.util.misc as misc
from contrib.util.executable import Executable


# ----------------------------- MODULE EXECUTION FUNCTIONS
def execmodule(module, mode, argv):
    """Execute python module in sandbox"""

    module.reset_state()
    reported_by = ' (reported by {0!r})'.format(module.filename)
    ns = {
 #       'user': user.user_env,
        'getenv': pymod.environ.get,
        'env': pymod.environ.copy(),
        'is_darwin': 'darwin' in sys.platform,
        'get_hostname': socket.gethostname,
        'mode': lambda: mode,
        'self': module,
        'colorize': colorize,
        #
        'parse_args': lambda: module.parse_args(argv),
        #
        'log_info': lambda s: logging.info(s, reported_by=module.filename),
        'log_warn': lambda s: logging.warn(s, reported_by=module.filename),
        'log_error': lambda s: logging.error(s, reported_by=module.filename),
        'execute': execute(mode),
        #
        'setenv': setenv(mode),
        'unsetenv': unsetenv(mode),
        #
        'use': use(mode),
        'unuse': unuse(mode),
        #
        'set_alias': set_alias(mode),
        'unset_alias': unset_alias(mode),
        #
        'set_shell_function': set_shell_function(mode),
        'unset_shell_function': unset_shell_function(mode),
        #
        'prereq': prereq(mode),
        'prereq_any': prereq_any(mode),
        'conflict': conflict(mode, module.name),
        #
        'load': load(mode),
        'swap': swap(mode),
        'load_first': load_first(mode),
        'unload': unload(mode),
        'is_loaded': is_loaded(mode),
        #
        'family': family(mode, module),
        #
        'prepend_path': prepend_path(mode),
        'append_path': append_path(mode),
        'remove_path': remove_path(mode),
        #
        'whatis': whatis(mode, module),
        'help': help(mode, module),
        'which': which,
        'check_output': check_output,
        #
        'source': source(mode),
    }

    # Execute the environment
    s = module.read(mode)
    code = compile(s, module.filename, 'exec')
    execfun(code, ns, {})


# ------------------- FUNCTIONS PASSED TO MODULE FILES ------------------ #
def execute(mode_):
    def _execute(command, mode=None):
        if mode is not None and mode != mode_:
            return
        xc = misc.split(command, ' ', 1)
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
                logging.warn('Command {0!r} failed'.format(command))
        return
    return _execute


def whatis(module):
    def _whatis(*args, **kwargs):
        module.set_whatis(*args, **kwargs)
    return _whatis


def help(mode, module):
    def _help(helpstr):
        module.set_helpstr(helpstr)
    return _help


def unload(mode):
    """Function to pass to modules to unload other modules"""
    def _unload(modulename):
        if mode == '*load*':
            return
        cb_unload(mode, modulename)
    return _unload


def load(mode):
    """Function to pass to modules to load other modules"""
    def _load(modulename, options=None):
        if mode == '*load*':
            return
        cb_load(mode, modulename, options=options)
    return _load


def swap(mode):
    """Function to pass to modules to load other modules"""
    def _swap(m1, m2):
        if mode == '*load*':
            return
        cb_swap(mode, m1, m2)
    return _swap


def load_first(mode):
    """Function to pass to modules to load other modules"""
    def mf_load_first(*modulenames):
        if mode == LOAD_PARTIAL:
            return
        cb_load(mode, load_first_of=modulenames)
    return _load_first


def is_loaded(mode):
    """Function to pass to modules to load other modules"""
    def _is_loaded(modulename):
        return cb_is_loaded(modulename)
    return _is_loaded


def source(mode):
    """Function to pass to modules to load other modules"""
    def _source(filename):
        return cb_source(mode, filename)
    return _source


def setenv(mode):
    """Set value of environment variable `name`"""
    def _setenv(name, value):
        if mode in ('load',):
            pymod.environ.setenv(name, value)
        elif mode in ('unload',):
            pymod.environ.unsetenv(name)
    return _setenv


def unsetenv(mode):
    """Set value of environment variable `name`"""
    def _unsetenv(name):
        if mode in ('load',):
            pymod.environ.unsetenv(name)
    return _unsetenv


def use(mode):
    def _use(path, append=False):
        if mode in ('load',):
            cb_use(path, append=append)
        elif mode in ('unload',):
            cb_unuse(path)
    return _use


def unuse(mode):
    """Set value of environment variable `name`"""
    def _unuse(path):
        if mode in ('load',):
            cb_unuse(path)
    return _unuse


def set_alias(mode):
    """Set value of environment variable `name`"""
    def _set_alias(name, value):
        if mode in ('load', '*load*'):
            pymod.environ.set_alias(name, value)
        elif mode in ('unload',):
            pymod.environ.unset_alias(name)
    return _set_alias


def unset_alias(mode):
    """Set value of environment variable `name`"""
    def _unset_alias(name):
        if mode in ('load', '*load*'):
            pymod.environ.unset_alias(name)
    return _unset_alias


def set_shell_function(mode):
    """Set value of environment variable `name`"""
    def _set_shell_function(name, value):
        if mode in ('load', '*load*'):
            pymod.environ.set_shell_function(name, value)
        elif mode in ('unload',):
            pymod.environ.unset_shell_function(name)
    return _set_shell_function


def unset_shell_function(mode):
    """Set value of environment variable `name`"""
    def mf_unset_shell_function(name):
        if mode in ('load', '*load*'):
            pymod.environ.unset_shell_function(name)
    return _unset_shell_function


def prereq_any(mode):
    def _prereq_any(*modulenames):
        if mode in ('load',):
            cb_prereq_any(*modulenames)
    return _prereq_any


def prereq(mode):
    def _prereq(*modulenames):
        if mode in ('load',):
            cb_prereq(*modulenames)
    return _prereq


def conflict(mode, name):
    def _conflict(*modulenames):
        if mode in ('load',):
            cb_conflict(name, *modulenames)
    return _conflict


def append_path(mode):
    """Append `value` to path-like variable `name`"""
    def _append_path(name, *values, **kwds):
        if mode in ('load',):
            cb_append_path(name, *values, **kwds)
        elif mode in ('unload',):
            cb_remove_path(name, *values, **kwds)
    return _append_path


def prepend_path(mode):
    """Prepend `value` to path-like variable `name`"""
    def _prepend_path(name, *values, **kwds):
        if mode in ('load',):
            cb_prepend_path(name, *values, **kwds)
        elif mode in ('unload',):
            cb_remove_path(name, *values, **kwds)
    return _prepend_path


def remove_path(mode):
    """Append `value` to path-like variable `name`"""
    def _remove_path(name, *values, **kwds):
        if mode in ('load',):
            cb_remove_path(name, *values, **kwds)
    return _remove_path


def family(mode, module):
    """Assign a family"""
    def _family(family_name):
        cb_family(mode, family_name, module)
    return _family
