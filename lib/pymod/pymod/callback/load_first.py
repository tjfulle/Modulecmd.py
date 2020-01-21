import pymod.mc
import pymod.modes
from pymod.error import ModuleNotFoundError

category = "module"


def load_first(module, mode, *names):
    """Load the first of modules in `names`

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        names (tuple of str): Names of modules to load

    Returns:
        loaded (Module): The loaded module

    Notes:
    - In load mode, loads the first available module in `names` and returns it. In \
            unload mode, the first loaded module in `names` is unloaded.

    - If no available modules are found in `names`, an error occurs

    - If the last of `names` is None, no error is thrown if no available \
            modules are found in `names`

    Examples:
    Consider the module ``baz``

    .. code-block:: python

        load_first('spam', 'eggs')

    On loading module ``baz``, the first available module of ``spam`` or ``eggs`` is loaded.

    .. code-block:: console

        $ module ls
        No loaded modules

        $ module load baz
        $ module ls
        Currently loaded modules
            1) eggs  2) baz

    The module ``eggs`` was loaded because ``spam`` was not available.

    """
    pymod.modes.assert_known_mode(mode)
    for name in names:
        if name is None:
            continue
        try:
            if mode == pymod.modes.unload:
                # We are in unload mode and the module was requested to be
                # loaded. So, we reverse the action and unload it
                return pymod.mc.unload(name, caller="load_first")
            else:
                return pymod.mc.load(name, caller="load_first")
        except ModuleNotFoundError:
            continue
    if names and name is None:
        return
    raise ModuleNotFoundError(",".join(names))
