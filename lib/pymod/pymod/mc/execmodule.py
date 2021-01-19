import os
import sys

import pymod.mc
import pymod.user
import pymod.modes
import pymod.module
import pymod.environ
import pymod.callback
import llnl.util.tty as tty
from llnl.util.filesystem import working_dir
from llnl.util.lang import Singleton

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
    tty.debug("Executing module {0} with mode {1}".format(module, mode))
    module.prepare()
    ns = module_exec_sandbox(module, mode)
    code = compile(module.read(mode), module.filename, "exec")
    with working_dir(os.path.dirname(module.filename)):
        try:
            if isinstance(module, pymod.module.TclModule):
                clone = pymod.environ.clone()
            exec_(code, ns, {})
        except pymod.error.StopLoadingModuleError:
            pass
        except pymod.error.TclModuleBreakError:
            # `break` command encountered.  we need to roll back changes to the
            # environment and tell whoever called not to register this module
            pymod.environ.restore(clone)
            module.exec_failed_do_not_register = True


def module_exec_sandbox(module, mode):
    callback = lambda cb, **kwds: pymod.callback.callback(cb, module, mode, **kwds)
    ns = {
        "os": os,
        "sys": sys,
        "env": pymod.environ.copy(include_os=True),
        "self": module,
        "user_env": pymod.user.env,
        "is_darwin": "darwin" in sys.platform,
        "IS_DARWIN": "darwin" in sys.platform,
        #
        "add_option": module.add_option,
        "opts": Singleton(module.parse_opts),
    }

    for fun in pymod.callback.all_callbacks():
        kwds = {}
        if fun.endswith(("set_alias", "set_shell_function", "getenv")):
            # when='always' because we may partially load a module just define
            # aliases and functions.  This is used by the clone capability that
            # can set environment variables from a clone, but cannot know what
            # aliases and functions existed in the clone.
            kwds["when"] = "always"
        elif fun == "whatis":
            # filter out this function if not in whatis mode
            kwds["when"] = mode == pymod.modes.whatis
        elif fun == "help":
            # filter out this function if not in help mode
            kwds["when"] = mode == pymod.modes.help
        else:
            # Let the function know nothing was explicitly set
            kwds["when"] = None
        ns[fun] = callback(fun, **kwds)
    return ns
