import modulecmd.xio as xio
import modulecmd.error

category = "utility"


def _break(module, mode):
    """Implementation of TCL module "break" command

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution

    Notes:
    If a TCL module issues the "break" command, all modifications done to the \
    environment up to that point are reversed, as if the module had never been \
    executed.

    """
    xio.warn("Evaluation of {0} aborted".format(module.fullname))
    raise modulecmd.error.TclModuleBreakError
