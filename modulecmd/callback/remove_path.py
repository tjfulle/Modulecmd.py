import os
import modulecmd.modes
import modulecmd.names
import modulecmd.environ
import modulecmd.callback

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
    Consider the module ``baz`` that removes `baz` from the path-like
    environment variable `BAZ`

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
    modulecmd.modes.assert_known_mode(mode)
    if name == modulecmd.names.modulepath:
        for value in values:
            modulecmd.callback.unuse.unuse(module, mode, value)
        return
    sep = kwds.get("sep", os.pathsep)
    if mode != modulecmd.modes.unload:
        for value in values:
            modulecmd.environ.remove_path(name, value, sep)
