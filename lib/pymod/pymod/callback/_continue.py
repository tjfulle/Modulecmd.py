import pymod.error

category = 'utility'


def _continue(module, mode):
    """Implementation of TCL module "continue" command

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution

    Notes:
    If a TCL module issues the "continue" command, evaluation of the module \
    stops, but the changes made up to that point are maintained.

    """
    raise pymod.error.StopLoadingModuleError
