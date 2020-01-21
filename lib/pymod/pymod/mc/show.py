import sys
import pymod.mc
import pymod.modes
import pymod.module
import pymod.callback
import pymod.modulepath
from pymod.error import ModuleNotFoundError


def show(name, opts=None, insert_at=None, mode="load"):
    """Show the commands that would result from loading module given by `name`

    Parameters
    ----------
    name : string_like
        Module name, full name, or file path
    insert_at : int
        Load the module as the `insert_at`th module.

    Raises
    ------
    ModuleNotFoundError

    """
    # Execute the module
    module = pymod.modulepath.get(name)
    if module is None:
        raise ModuleNotFoundError(name, mp=pymod.modulepath)

    # Set the command line options
    if opts:
        module.opts = opts

    # Now execute it
    pymod.mc.execmodule(module, pymod.modes.show)

    # and show it
    sys.stderr.write(pymod.mc.cur_module_command_his.getvalue())
