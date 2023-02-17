import modulecmd.system
import modulecmd.modes
from modulecmd.error import ModuleNotFoundError

category = "module"


def load(module, mode, name, **kwds):
    """Load the module `name`

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        name (str): Name of module to load

    Keyword arguments:
        opts (dict): Module options


    Notes:
    - In load mode, loads the module found by `name` if it is not already loaded. \
            If it is loaded, its internal reference count is incremented.

    - In unload mode, decrements the reference count of the module found by \
            `name`.  If the reference count gets to 0, the module is unloaded.

    Examples:
    Consider the module ``baz``

    .. code-block:: python

        load('spam', opts={'x': True})

    On loading module ``baz``, the module ``spam``, if available, is loaded with options
    ``opts``.

    .. code-block:: console

        $ module ls
        No loaded modules

        $ module load baz
        $ module ls
        Currently loaded modules
            1) eggs x=True  2) baz

    """
    modulecmd.modes.assert_known_mode(mode)
    opts = kwds.get("opts", None)
    modulecmd.modes.assert_known_mode(mode)
    if mode == modulecmd.modes.unload:
        # We are in unload mode and the module was requested to be loaded.
        # So, we reverse the action and unload it
        try:
            modulecmd.system.unload(name, caller="modulefile")
        except ModuleNotFoundError:
            return
    else:
        modulecmd.system.load(name, opts=opts, caller="modulefile")
