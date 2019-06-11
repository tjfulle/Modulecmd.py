import pymod.mc
import pymod.modes

category = 'family'


def family(module, mode, family_name):
    """Defines the "family" of the module

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        family_name (str): Name of the family

    Notes:
    - Only one module in a family can be loaded at a time.  For instance, GCC and \
      Intel compiler modules can define their family as "compiler".  This prevents \
      GCC and Intel compilers being loaded simultaneously.

    - This function potentially has side effects on the environment.  When \
      a module is loaded, if a module of the same family is already loaded, they \
      will be swapped.  Swapping has the potential to change the ``MODULEPATH`` and \
      state of loaded modules.

    Examples:
    Consider modules ``ucc`` and ``xcc`` that are both members of the ``compiler`` family.
    The module ``ucc/1.0`` is already loaded

    .. code-block:: console

        $ module ls
        Currently loaded modules
            1) ucc/1.0

    On loading ``xcc/1.0``, ``ucc/1.0`` is unloaded

    .. code-block:: console

        $ module load xcc/1.0

        The following modules in the same family have been updated with a version change:
          1) ucc/1.0 => xcc/1.0 (compiler)

    """
    pymod.modes.assert_known_mode(mode)
    pymod.mc.family(module, mode, family_name)
