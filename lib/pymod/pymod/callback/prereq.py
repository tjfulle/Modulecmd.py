import pymod.mc
import pymod.modes

category = 'interaction'


def prereq(module, mode, *names):
    """Defines a prerequisite (module that must be loaded) for this module

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        names (tuple of str): Names of prerequisite modules

    Notes:
    In load mode, asserts that every `name` in `names` is loaded.  Otherwise, nothing is done.

    Examples:
    Consider the module ``baz``

    .. code-block:: python

        prereq('spam', 'eggs')

    If any ``spam`` or ``eggs`` is not loaded, an error occurs:

    .. code-block:: console

        $ module ls
        Currently loaded module
            1) spam

        $ module load baz
        ==> Error: Prerequisite 'eggs' must first be loaded

    """
    # FIXME: This function should execute mc.prereq in any mode other than
    # unload.  In whatis, help, show, etc. modes, it should register the prereqs
    # but not enforce them.
    pymod.modes.assert_known_mode(mode)
    if mode == pymod.modes.load:
        pymod.mc.prereq(*names)
