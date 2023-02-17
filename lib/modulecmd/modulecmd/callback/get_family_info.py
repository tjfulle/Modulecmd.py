import modulecmd.modes
import modulecmd.names
import modulecmd.environ

category = "family"


def get_family_info(module, mode, name, **kwargs):
    """Returns information about family `name`

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        name (str): The name of the family to get information about

    Returns:
        family_name (str): The module name in family `name`
        version (str): The version of the module in family `name`

    Notes:
    If a module of family `name` is loaded, this function returns its name and
    version.  Otherwise, the name and version return as `None`

    Examples:
    The following module performs actions if the compiler ``ucc`` is loaded

    .. code-block:: python

        name, version = get_family_info('compiler')
        if name == 'ucc':
            # Do something specific if ucc is loaded

    """
    modulecmd.modes.assert_known_mode(mode)
    name_envar = modulecmd.names.family_name(name)
    version_envar = modulecmd.names.family_version(name)
    return modulecmd.environ.get(name_envar), modulecmd.environ.get(version_envar)
