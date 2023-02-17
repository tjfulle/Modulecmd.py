import modulecmd.system
import modulecmd.modes
from modulecmd.error import ModuleNotFoundError

category = "module"


def unload(module, mode, name):
    """Unload the module `name`

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        name (str): Name of the module to unload

    Notes:
    - In load mode, decrements the reference count of the module found by `name`. \
            If the reference count drops to 0, the module is unloaded.

    - If the module is not found, or is not loaded, nothing is done.

    - In unload mode, nothing is done.

    Examples:
    Consider the module ``baz``

    .. code-block:: python

        unload('spam')

    On loading ``baz``, the module ``spam`` is unloaded (if it is already loaded)

    .. code-block:: console

        $ module ls
        Currently loaded modules
            1) spam

        $ module load baz
        Currently loaded modules
            1) baz

    """
    modulecmd.modes.assert_known_mode(mode)
    if mode == modulecmd.modes.unload:
        # We are in unload mode and the module was requested to be
        # unloaded. But, we don't know if it was previously loaded. So we
        # skip
        return
    else:
        try:
            modulecmd.system.unload(name, caller="modulefile")
        except ModuleNotFoundError:
            return None
