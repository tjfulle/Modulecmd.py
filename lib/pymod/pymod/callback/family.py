import pymod.mc
import pymod.modes

category = ''


def family(module, mode, family_name, **kwargs):
    """Defines the "family" of the module

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    family_name : str
        Name of the family

    Notes
    -----
    Only one module in a family can be loaded at a time.  For instance, GCC and
    Intel compiler modules can define their family as "compiler".  This prevents
    GCC and Intel compilers being loaded simultaneously.

    This function potentially has side effects on the environment.  When
    a module is loaded, if a module of the same family is already loaded, they
    will be swapped.  Swapping has the potential to change the MODULEPATH and
    state of loaded modules.

    """
    pymod.modes.assert_known_mode(mode)
    pymod.mc.family(module, mode, family_name)