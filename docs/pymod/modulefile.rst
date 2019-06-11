.. _modulefiles:

===========
Modulefiles
===========

----------
References
----------

- :ref:`the-modulepath`

--------
Overview
--------

Module files are python scripts that are executed by the `Modulecmd.py`_ framework.  Modulefiles

- have a ``.py`` file extension;
- must exist on the :ref:`basic-usage-modulepath` to be found; and
- are executed by `Modulecmd.py`_ in a sandboxed environment.

For compatibility with existing systems, `Modulecmd.py`_ can execute TCL
modulefiles, but they are not covered in this guide.

------------------
Naming conventions
------------------

Several naming conventions are supported:

- name only;
- name/version; and
- name/version/variant.

^^^^^^^^^
Name only
^^^^^^^^^

In the name only naming convention, a module's name, version, and other information is embedded directly in the module's name.  For instance, a module ``baz``, version ``1.0`` might be named: ``<prefix>/baz-1.0.py``, where ``prefix`` is a path on the ``MODULEPATH``.  This naming convention is common with TCL modules but prevents some `Modulecmd.py`_ features from being effectuated, such as the :ref:`one-name-rule`.

^^^^^^^^^^^^
Name/version
^^^^^^^^^^^^

In the name/version convention, the name of a module is given by a directory ``<name>`` and its version by the python script ``<version>.py``.  For example, the module ``baz``, version ``1.0`` would be: ``<prefix>/baz/1.0.py``, where ``prefix`` is a path on the ``MODULEPATH``.

.. note::

  This name/version convention is the preferred naming convention for `Modulecmd.py`_.

^^^^^^^^^^^^^^^^^^^^
Name/version/variant
^^^^^^^^^^^^^^^^^^^^

In the name/version/variant convention,  the module ``baz``, version ``1.0``, with variant ``a`` would be named: ``<prefix>/baz/1.0/a.py``, where ``prefix`` is a path on the ``MODULEPATH``.

---------------
Module commands
---------------

`Modulecmd.py`_ executes module files in an environment providing many commands
for interacting with the shell's environment.

.. <INSERT HERE>

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Functions for modifying path-like variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**append_path**\ *(name, \*values, \*\*kwargs)*

    Append `values` to path-like variable `name`

    **Arguments**

    *name* (str): Name of path-like variable
    *values* (tuple of str): The values to append to path-like variable `name`

    **Keyword arguments**

    *sep* (str): defines the separator between values in path-like variable `name` (default is os.pathsep)

    **Notes**

    - In *unload* mode, `values` are removed from path-like variable `name`,       otherwise, they are appended.

    - If ``name==MODULEPATH``, this function calls ``use(value, append=True)``       for each `value` in `values`.

    - A path-like variable stores a list as a ``sep`` separated string.  eg, the       PATH environment variable is a ``sep`` separated list of directories:

      .. code-block:: console

          $ echo ${PATH}
          dirname1:dirname2:...

    Here, ":" is the separator ``sep``.


    **Examples**

    Consider the module ``baz``

    .. code-block:: python

        # Append `baz` to the path-like environment variable `BAZ`
        append_path('BAZ', 'baz')

    .. code-block:: console

        $ echo ${BAZ}
        spam

    .. code-block:: console

        $ module load baz

    .. code-block:: console

        $ echo ${BAZ}
        spam:baz

.. <END INSERT HERE>

--------------
Module Options
--------------
A module can support command line options.  Options are specified on the command line as

.. code-block:: console

  module load <modulename> [+option[=value] [+option...]]

The following modulefile functions register options

``add_option(name, action='store_true')``
    Register a module option.  By default, options are boolean flags.  Pass ``action='store'`` to register an option that takes a value.

``parse_opts()``
    Parse module options.  Only options added before calling ``parse_opts`` will be parsed.


^^^^^^^^
Examples
^^^^^^^^

To specify two options for module 'spam', in modulefile spam.py do

.. code-block:: python

  add_option('+x', action='store')  # option with value
  add_option('+b')  # boolean option
  opts = parse_opts()

  if (opts.b):
      # Do something
  if (opts.x == 'baz'):
      # Do something

On the commandline, the module spam can be loaded as

.. code-block:: console

  module load spam +b +x=baz

--------------
Other Commands
--------------

``family(name)``
    Set the name of the module's family.

``execute(command)``
    Execute command in the current shell.

``whatis(string)``
    Store string as an informational message describing this module.


^^^^^^^^
Examples
^^^^^^^^

The following commands, when put in a module file on ``MODULEPATH``, prepends the user's bin directory to the ``PATH`` and aliases the ``ls`` command.

.. code-block:: python

  prepend_path('PATH', '~/bin')
  set_alias('ls', 'ls -lF')

.. _Modulecmd.py: https://www.github.com/tjfulle/Modulecmd.py
