import modulecmd.system
import modulecmd.modes

category = "interaction"


def prereq_any(module, mode, *names):
    """Defines prerequisites (modules that must be loaded) for this module

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        names (tuple of str): Names of prerequisite modules

    Notes:
    In load mode, asserts that at least one of the modules given by `names` is
    loaded.  Otherwise, nothing is done.

    Examples:
    Consider the module ``baz``

    .. code-block:: python

        prereq_any('spam', 'eggs')

    If any ``spam`` or ``eggs`` is not loaded, an error occurs:

    .. code-block:: console

        $ module ls
        Currently loaded module
            1) ham

        $ module load baz
        ==> Error: One of the prerequisites 'spam,eggs' must first be loaded

    """
    # FIXME: This function should execute mc.prereq_any in any mode other than
    # unload.  In whatis, help, show, etc. modes, it should register the prereqs
    # but not enforce them.
    modulecmd.modes.assert_known_mode(mode)
    if mode == modulecmd.modes.load:
        modulecmd.system.prereq_any(*names)
