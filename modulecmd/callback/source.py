import modulecmd.system
import modulecmd.modes

category = "utility"


def source(module, mode, filename, *args):
    """Sources a shell script given by filename

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        filename (str): Name of the filename to source

    Notes:
    - **Warning:** This function sources a shell script unconditionally.  Environment \
            modifications made by the script are not tracked by Modulecmd.py.

    - `filename` is sourced only if ``mode()=='load'`` and is only sourced once

    """
    modulecmd.modes.assert_known_mode(mode)
    if mode == modulecmd.modes.load:
        modulecmd.system.source(filename, *args)
