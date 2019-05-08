import sys
import pymod.mc
import pymod.modes
import pymod.modulepath

from pymod.mc.execmodule import execmodule
from pymod.error import ModuleNotFoundError


def show(name, opts=None, insert_at=None):
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

    # Now load it
    execmodule(module, pymod.modes.show)
    pymod.mc.dump(stream=sys.stderr)
