import os
import sys
import socket

import pymod.mc
import pymod.user
import pymod.modes
import pymod.environ
import pymod.callback
import llnl.util.tty as tty
from llnl.util.filesystem import working_dir

from six import exec_
from pymod.error import FamilyLoadedError


# ----------------------------- MODULE EXECUTION FUNCTIONS
def execmodule(module, mode):
    """Execute the module in a sandbox"""
    assert module.acquired_as is not None
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
    with working_dir(os.path.dirname(module.filename)):
        try:
            exec_(code, ns, {})
        except pymod.error.StopLoadingModuleError:
            pass


def module_exec_sandbox(module, mode):
    callback = lambda cb, **kwds: pymod.callback.callback(cb, module, mode, **kwds)
    ns = {
        'os': os,
        'sys': sys,
        'self': module,
        'user_env': pymod.user.env,
        'getenv': pymod.environ.get,
        'get_hostname': socket.gethostname,
        'is_darwin': 'darwin' in sys.platform,
        'IS_DARWIN': 'darwin' in sys.platform,
        'env': pymod.environ.copy(include_os=True),
        'mode': lambda: pymod.modes.as_string(mode),
        #
        'add_option': module.parser.add_argument,
        'parse_opts': module.parse_args,
        #
        'log_info': lambda s: tty.info(s, reported_by=module.fullname),
        'log_warning': lambda s: tty.warn(s, reported_by=module.fullname),
        'log_error': lambda s: tty.die(s, reported_by=module.fullname),
        #
        'stop': callback('stop'),
        'which': callback('which'),
        'mkdirp': callback('mkdirp'),
        'source': callback('source'),
        'execute': callback('execute'),
        'listdir': callback('listdir'),
        'colorize': callback('colorize'),
        'check_output': callback('check_output'),
        #
        'setenv': callback('setenv'),
        'unsetenv': callback('unsetenv'),
        #
        'use': callback('use'),
        'unuse': callback('unuse'),
        #
        'set_alias': callback('set_alias', when='alsways'),
        'unset_alias': callback('unset_alias', when='always'),
        #
        'set_shell_function': callback('set_shell_function', when='always'),
        'unset_shell_function': callback('unset_shell_function', when='always'),
        #
        'prereq': callback('prereq'),
        'prereq_any': callback('prereq_any'),
        'conflict': callback('conflict'),
        #
        'load': callback('load'),
        'swap': callback('swap'),
        'load_first': callback('load_first'),
        'unload': callback('unload'),
        'is_loaded': callback('is_loaded'),
        #
        'family': callback('family'),
        'get_family_info': callback('get_family_info'),
        #
        'prepend_path': callback('prepend_path'),
        'append_path': callback('append_path'),
        'remove_path': callback('remove_path'),
        #
        'whatis': callback('whatis', when=mode==pymod.modes.whatis),
        'help': callback('help', when=mode==pymod.modes.help),
    }
    return ns
