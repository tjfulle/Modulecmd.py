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

from six import exec_, StringIO
from pymod.error import FamilyLoadedError


# ----------------------------- MODULE EXECUTION FUNCTIONS
def execmodule(module, mode):
    """Execute the module in a sandbox"""
    assert module.acquired_as is not None
    pymod.modes.assert_known_mode(mode)

    # Enable logging of commands in this module
    pymod.mc.cur_module_command_his = StringIO()

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
        'get_hostname': socket.gethostname,
        'is_darwin': 'darwin' in sys.platform,
        'IS_DARWIN': 'darwin' in sys.platform,
        'mode': lambda: pymod.modes.as_string(mode),
        #
        'add_option': module.add_option,
        'parse_opts': module.parse_opts,
    }
    for fun in pymod.callback.all_callbacks():
        kwds = {}
        if fun.endswith(('set_alias', 'set_shell_function')):
            kwds['when'] = 'always'
        elif fun == 'whatis':
            kwds['when'] = mode == pymod.modes.whatis
        elif fun == 'help':
            kwds['when'] = mode == pymod.modes.help
        ns[fun] = callback(fun, **kwds)
    return ns
