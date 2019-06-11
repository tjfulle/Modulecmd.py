import pymod.mc
import pymod.modes

category = 'modulepath'


def use(module, mode, dirname, append=False):
    """Add the directory `dirname` to ``MODULEPATH``

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        dirname (str): Name of the directory to add to ``MODULEPATH``

    Keyword arguments:
        append (bool): Append `dirname` to ``MODULEPATH``, otherwise `dirname` \
                is prepended.  The default is ``False``.

    Notes:
    In load mode, adds `dirname` to the ``MODULEPATH``.  In unload mode, remove
    `dirname` from the ``MODULEPATH`` (if it is on ``MODULEPATH``).

    This function potentially has side effects on the environment.  When
    a directory is ``use``\ d, modules in its path may have higher precedence than
    modules on the previous ``MODULEPATH``.  Thus, defaults could change and loaded
    modules could be swapped for newer modules with higher precedence.

    """
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.unload:
        pymod.mc.unuse(dirname)
    else:
        pymod.mc.use(dirname, append=append)
        module.unlocks_dir(dirname)
