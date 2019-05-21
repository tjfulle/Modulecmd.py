import pymod.mc
import pymod.modes
import pymod.module
import pymod.modulepath
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

    if isinstance(module, pymod.module.TclModule):
        pymod.mc.execmodule(module, pymod.modes.show)
    else:
        # Now load it
        pymod.mc.execmodule(module, pymod.modes.load)
