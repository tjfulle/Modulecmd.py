import pymod.modes
import pymod.modulepath

category = 'info'


def is_loaded(module, mode, name):
    """Report whether the module `name` is loaded

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        name (str): Name of the module to report

    Returns:
        is_loaded (bool): Whether the module given by `name` is loaded

    Examples:

    .. code-block:: python

        if is_loaded('baz'):
            # Do something if baz is loaded
            ...

    """
    pymod.modes.assert_known_mode(mode)
    other = pymod.modulepath.get(name)
    if other is None:
        return None
    return other.is_loaded
