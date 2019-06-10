import os
import pymod.modes
import pymod.names
import pymod.environ
import pymod.callback

category = ''


def prepend_path(module, mode, name, *values, **kwds):
    """Prepend `values` to path-like variable `name`

    Parameters
    ----------
    module : Module
        The module being executed
    mode : Mode
        The mode of execution
    name : str
        Name of path-like variable
    values : tuple of str
        The values to prepend to path-like variable `name`
    kwds : dict
        kwds['sep'] defines the separator between values in path-like variable
        `name`.  Defaults to os.pathsep

    Notes
    -----
    In unload mode, `values` are removed from path-like variable `name`,
    otherwise, they are prepended.

    If `name==MODULEPATH`, this function calls `use(value)` for each
    `value` in `values`.

    A path-like variable stores a list as a `sep` separated string.  eg, the
    PATH environment variable is a `sep` separated list of directories:

        echo $PATH
        dirname1:dirname2:...

    Here, ":" is the separator `sep`.

    """
    pymod.modes.assert_known_mode(mode)
    if name == pymod.names.modulepath:
        for value in values:
            pymod.callback.use.use(module, mode, value)
        return
    sep = kwds.get('sep', os.pathsep)
    if mode == pymod.modes.unload:
        for value in values:
            pymod.environ.remove_path(name, value, sep)
    else:
        for value in values:
            pymod.environ.prepend_path(name, value, sep)
