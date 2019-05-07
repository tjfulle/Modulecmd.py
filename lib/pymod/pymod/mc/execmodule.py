import os
import sys
import socket
import subprocess

import pymod.mc
import pymod.modes
import pymod.environ
import llnl.util.tty as tty
from contrib.util import which, check_output

from pymod.mc.callback import callback
from llnl.util.tty.color import colorize
from spack.util.executable import Executable
from six import exec_
from pymod.error import FamilyLoadedError


# ----------------------------- MODULE EXECUTION FUNCTIONS
def execmodule(module, mode, do_not_register=False):
    """Execute the module in a sandbox"""
    pymod.modes.assert_known_mode(mode)
    try:
        out = execmodule_impl(module, mode,
                              do_not_register=do_not_register)

        if mode == pymod.modes.load:
            pymod.mc.set_refcount(module, 1)
        elif mode in (pymod.modes.unload,):
            pymod.mc.pop_refcount(module)

        return out

    except FamilyLoadedError as e:
        # Module of same family already loaded, unload it first

        # This comes after first trying to load the module because the
        # family is set within the module, so the module must first be
        # loaded to determine the family. If when the family is being set
        # it is discovered that a module from the same family is loaded,
        # the FamilyLoadedError is raised.

        # This should only happen in load mode
        assert mode == pymod.modes.load
        other = pymod.modulepath.get(e.args[0])
        pymod.mc.swapped_on_family_update(other, module)
        assert other.is_loaded
        pymod.mc.swap_impl(other, module)


def execmodule_impl(module, mode, do_not_register=False):
    """Execute filename in sandbox"""

    if module.type not in (pymod.module.python, pymod.module.tcl):
        tty.die('Module {0!r} has unknown module type: '
                      '{1!r}'.format(module.fullname, module.type))

    try:
        execmodule_in_sandbox(module, mode)
    except FamilyLoadedError as e:
        raise e
    else:
        if mode == pymod.modes.load:
            pymod.mc.on_module_load(module, do_not_register=do_not_register)
        elif mode in (pymod.modes.unload,):
            pymod.mc.on_module_unload(module)

    return None


def execmodule_in_sandbox(module, mode):
    """Execute python module in sandbox"""

    module.reset_state()

    # Execute the environment
    ns = module_exec_sandbox(module, mode)
    code = compile(module.read(mode), module.filename, 'exec')
    exec_(code, ns, {})



def module_exec_sandbox(module, mode):
    reported_by = ' (reported by {0!r})'.format(module.filename)
    ns = {
        'os': os,
        'sys': sys,
 #       'user': user.user_env,
        'getenv': pymod.environ.get,
        'is_darwin': 'darwin' in sys.platform,
        'IS_DARWIN': 'darwin' in sys.platform,
        'get_hostname': socket.gethostname,
        'mode': lambda: mode,
        'self': module,
        'colorize': colorize,
        #
        'add_option': module.parser.add_argument,
        'parse_opts': module.parse_args,
        #
        'log_info': lambda s: tty.info(s, reported_by=module.filename),
        'log_warn': lambda s: tty.warn(s, reported_by=module.filename),
        'log_error': lambda s: tty.die(s, reported_by=module.filename),
        'execute': callback('execute', mode),
        #
        'setenv': callback('setenv', mode),
        'unsetenv': callback('unsetenv', mode),
        #
        'use': callback('use', mode),
        'unuse': callback('unuse', mode),
        #
        'set_alias': callback('set_alias', mode),
        'unset_alias': callback('unset_alias', mode),
        #
        'set_shell_function': callback('set_shell_function', mode),
        'unset_shell_function': callback('unset_shell_function', mode),
        #
        'prereq': callback('prereq', mode),
        'prereq_any': callback('prereq_any', mode),
        'conflict': callback('conflict', mode, module),
        #
        'load': callback('load', mode),
        'swap': callback('swap', mode),
        'load_first': callback('load_first', mode),
        'unload': callback('unload', mode),
        'is_loaded': callback('is_loaded', mode),
        #
        'family': callback('family', mode, module),
        #
        'prepend_path': callback('prepend_path', mode),
        'append_path': callback('append_path', mode),
        'remove_path': callback('remove_path', mode),
        #
        'whatis': callback('whatis', mode, module),
        'help': callback('help', mode, module),
        'which': which,
        'check_output': check_output,
        #
        'source': callback('source', mode),
    }
    return ns