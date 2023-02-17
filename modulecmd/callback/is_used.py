import modulecmd.modulepath

category = "modulepath"


def is_used(module, mode, dirname):
    """Returns whether the directory `dirname` is on the ``MODULEPATH``

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        dirname (str): Name of the directory to check

    Returns:
        is_used (bool): Wether `dirname` is on the ``MODULEPATH`` or not

    """
    modulecmd.modes.assert_known_mode(mode)
    return modulecmd.modulepath.contains(dirname)
