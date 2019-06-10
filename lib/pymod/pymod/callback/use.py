import pymod.mc
import pymod.modes

category = 'modulepath'


def use(module, mode, dirname, append=False):
    """Add the directory `dirname` to MODULEPATH

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    dirname : str
        Name of the directory to add to MODULEPATH
    append : bool {False}
        Append `dirname` to MODULEPATH, otherwise `dirname` is preprended

    Notes
    -----
    In load mode, add `dirname` to MODULEPATH.  In unload mode, remove
    `dirname` from MODULEPATH (if it is on MODULEPATH).

    This function potentially has side effects on the environment.  When
    a directory is `use`d, modules in its path may have higher precedence than
    modules on the previous MODULEPATH.  Thus, defaults could change and loaded
    modules could be swapped for newer modules with higher precedence.

    """
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.unload:
        pymod.mc.unuse(dirname)
    else:
        pymod.mc.use(dirname, append=append)
        module.unlocks_dir(dirname)
