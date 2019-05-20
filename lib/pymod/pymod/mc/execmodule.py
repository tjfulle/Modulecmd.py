import os
import sys
import socket

import pymod.mc
import pymod.user
import pymod.modes
import pymod.environ
import pymod.mc.callback
import llnl.util.tty as tty
from contrib.util import which, check_output, listdir

from llnl.util.tty.color import colorize
from llnl.util.filesystem import mkdirp
from six import exec_
from pymod.error import FamilyLoadedError


# ----------------------------- MODULE EXECUTION FUNCTIONS
def execmodule(module, mode):
    """Execute the module in a sandbox"""
    pymod.modes.assert_known_mode(mode)

    try:
        return execmodule_in_sandbox(module, mode)

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


def execmodule_in_sandbox(module, mode):
    """Execute python module in sandbox"""

    # Execute the environment
    module.prepare()
    ns = module_exec_sandbox(module, mode)
    code = compile(module.read(mode), module.filename, 'exec')
    try:
        exec_(code, ns, {})
    except StopLoadingModuleError:
        pass


def module_exec_sandbox(module, mode):
    def stop():
        raise StopLoadingModuleError
    cb = pymod.mc.callback
    callback = pymod.mc.callback.callback
    ns = {
        'os': os,
        'sys': sys,
        'stop': stop,
        'mkdirp': mkdirp,
        'env': pymod.environ.copy(include_os=True),
        'user_env': pymod.user.env,
        'getenv': pymod.environ.get,
        'is_darwin': 'darwin' in sys.platform,
        'IS_DARWIN': 'darwin' in sys.platform,
        'get_hostname': socket.gethostname,
        'listdir': lambda dirname, key=None: listdir(dirname, key=key),
        'mode': lambda: mode,
        'self': module,
        'colorize': colorize,
        #
        'add_option': module.parser.add_argument,
        'parse_opts': module.parse_args,
        #
        'log_info': lambda s: tty.info(s, reported_by=module.fullname),
        'log_warning': lambda s: tty.warn(s, reported_by=module.fullname),
        'log_error': lambda s: tty.die(s, reported_by=module.fullname),
        'execute': callback(cb.execute, mode, module),
        #
        'setenv': callback(cb.setenv, mode, module),
        'unsetenv': callback(cb.unsetenv, mode, module),
        #
        'use': callback(cb.use, mode, module),
        'unuse': callback(cb.unuse, mode, module),
        #
        'set_alias': callback(cb.set_alias, mode, module, when='alsways'),
        'unset_alias': callback(cb.unset_alias, mode, module, when='always'),
        #
        'set_shell_function': callback(cb.set_shell_function, mode, module, when='always'),
        'unset_shell_function': callback(cb.unset_shell_function, mode, module, when='always'),
        #
        'prereq': callback(cb.prereq, mode, module),
        'prereq_any': callback(cb.prereq_any, mode, module),
        'conflict': callback(cb.conflict, mode, module),
        #
        'load': callback(cb.load, mode, module),
        'swap': callback(cb.swap, mode, module),
        'load_first': callback(cb.load_first, mode, module),
        'unload': callback(cb.unload, mode, module),
        'is_loaded': callback(cb.is_loaded, mode, module),
        #
        'family': callback(cb.family, mode, module),
        #
        'prepend_path': callback(cb.prepend_path, mode, module),
        'append_path': callback(cb.append_path, mode, module),
        'remove_path': callback(cb.remove_path, mode, module),
        #
        'whatis': callback(cb.whatis, mode, module, when=mode==pymod.modes.whatis),
        'help': callback(cb.help, mode, module, when=mode==pymod.modes.help),
        'which': which,
        'check_output': check_output,
        #
        'source': callback(cb.source, mode, module),
    }
    return ns


class StopLoadingModuleError(Exception):
    pass
