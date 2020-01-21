import os
import pymod.modes
import pymod.names
import pymod.environ
import pymod.callback

category = "path"


def remove_path(module, mode, name, *values, **kwds):
    """Removes `values` from the path-like variable `name`

    Arguments:
        module (Module): The module being executed
        mode (Mode): The mode of execution
        name (str): Name of path-like variable
        values (tuple of str): The values to remove from the path-like variable `name`

    Keyword arguments:
        sep (str): defines the separator between values in path-like variable \
            `name`  (default is os.pathsep)

    Notes:
    - In *unload* mode, nothing is done.  Otherwise, `values` are removed from \
      path-like variable `name`.

    - If ``name==MODULEPATH``, this function calls ``unuse(value)`` \
      for each `value` in `values`.

    - A path-like variable stores a list as a ``sep`` separated string.  eg, the \
      PATH environment variable is a ``sep`` separated list of directories:

      .. code-block:: console

          $ echo ${PATH}
          dirname1:dirname2:...

    Here, ":" is the separator ``sep``.

    Examples:
    Consider the module ``baz`` that removes `baz` from the path-like environment variable `BAZ`

    .. code-block:: python

        remove_path('BAZ', 'baz')

    The environment variable ``BAZ`` is currently

    .. code-block:: console

        $ echo ${BAZ}
        baz:spam

    On loading the module ``baz``, the environment variable ``BAZ`` is updated:

    .. code-block:: console

        $ module load baz
        $ echo ${BAZ}
        spam

    """
    pymod.modes.assert_known_mode(mode)
    if name == pymod.names.modulepath:
        for value in values:
            pymod.callback.unuse.unuse(module, mode, value)
        return
    sep = kwds.get("sep", os.pathsep)
    if mode != pymod.modes.unload:
        for value in values:
            pymod.environ.remove_path(name, value, sep)
