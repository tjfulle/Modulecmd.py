import pymod.modes
import pymod.names
import pymod.environ

category = ''


def get_family_info(module, mode, name, **kwargs):
    """Returns information about family `name`

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    name : str
        The name of the family to get information about

    Returns
    -------
    str
        The module name in family `name`
    str
        The version of the module in family `name`

    Notes
    -----
    If a module of family `name` is loaded, this function returns its name and
    version.  Otherwise, the name and version return as `None`

    """
    pymod.modes.assert_known_mode(mode)
    name_envar = pymod.names.family_name(name)
    version_envar = pymod.names.family_version(name)
    return pymod.environ.get(name_envar), pymod.environ.get(version_envar)