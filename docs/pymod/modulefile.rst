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

**append_path**\ *(name, \*values, \*\*kwds)*
    Append `values` to path-like variable `name`

    In unload mode, `values` are removed from path-like variable `name`,
    otherwise, they are appended.

    If ``name==MODULEPATH``, this function calls ``use(value, append=True)`` for
    each `value` in `values`.

    A path-like variable stores a list as a ``sep`` separated string.  eg, the
    PATH environment variable is a ``sep`` separated list of directories:

    .. code-block:: console

        echo $PATH
        dirname1:dirname2:...

    Here, ":" is the separator ``sep``.


**prepend_path**\ *(name, \*values, \*\*kwds)*
    Prepend `values` to path-like variable `name`

    In unload mode, `values` are removed from path-like variable `name`,
    otherwise, they are prepended.

    If ``name==MODULEPATH``, this function calls ``use(value)`` for each `value`
    in `values`.

    A path-like variable stores a list as a ``sep`` separated string.  eg, the
    PATH environment variable is a ``sep`` separated list of directories:

    .. code-block:: console

        echo $PATH
        dirname1:dirname2:...

    Here, ":" is the separator ``sep``.


**remove_path**\ *(name, \*values, \*\*kwds)*
    Removes `values` from path-like variable `name`

    In unload mode, nothing is done.  Otherwise, `values` are removed from path-
    like variable `name`.

    If ``name==MODULEPATH``, this function calls ``unuse(value)`` for each
    `value` in `values`.

    A path-like variable stores a list as a ``sep`` separated string.  eg, the
    PATH environment variable is a ``sep`` separated list of directories:

    .. code-block::

        echo $PATH
        dirname1:dirname2:...

    Here, ":" is the separator `sep`.


^^^^^^^^^^^^^^^^^^^^^^^^^
General purpose utilities
^^^^^^^^^^^^^^^^^^^^^^^^^

**check_output**\ *(command)*
    Run command with arguments and return its output as a string.

    This is a wrapper to `contrib.util.check_output`.  Where
    `subprocess.check_output` exists, it is called.  Otherwise, an
    implementation of `subprocess.check_output` is provided.


**colorize**\ *(string, \*\*kwargs)*
    Replace all color expressions in a string with ANSI control codes.

    This is a wrapper to `llnl.util.tty.color.colorize`.


**execute**\ *(command, when=None)*
    Executes the command `command` in a subprocess


**listdir**\ *(dirname, key=None)*
    List contents of directory `dirname`


**mkdirp**\ *(\*paths, \*\*kwargs)*
    Make directory `dir` and all intermediate directories, if necessary.

    This is a wrapper to `llnl.util.filesystem.mkdirp`.


**source**\ *(filename)*
    Sources a shell script given by filename

    Warning: this function sources a shell script unconditionally.  Environment
    modifications made by the script are not tracked by Modulecmd.py.

    `filename` is only sourced in load mode and is only sourced once


**stop**\ *()*
    Stop loading this module

    All commands up to the call to `stop` are executed.


**which**\ *(exename)*
    Return the path to an executable, if found on PATH

    This is a wrapper to `contib.util.which`.


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Functions for interacting with other modules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**conflict**\ *(\*names, \*\*kwargs)*
    Defines conflicts (modules that conflict with `module`)

    In load mode, asserts that none of `names` is loaded.   Otherwise, nothing
    is done.

    FIXME: This function should execute mc.conflict in any mode other than
    unload.  In whatis, help, show, etc. modes, it should register the conflicts
    but not enforce them.


**prereq**\ *(\*names)*
    Defines a prerequisite (module that must be loaded) for this module

    In load mode, asserts that `name` is loaded.  Otherwise, nothing is done.

    FIXME: This function should execute mc.prereq in any mode other than unload.
    In whatis, help, show, etc. modes, it should register the prereqs but not
    enforce them.


**prereq_any**\ *(\*names)*
    Defines prerequisites (modules that must be loaded) for this module

    In load mode, asserts that at least one of the modules given by `names` is
    loaded.  In unload mode, nothing is done.

    FIXME: This function should execute mc.prereq_any in any mode other than
    unload.  In whatis, help, show, etc. modes, it should register the prereqs
    but not enforce them.


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Functions for interacting with module families
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**family**\ *(family_name, \*\*kwargs)*
    Defines the "family" of the module

    Only one module in a family can be loaded at a time.  For instance, GCC and
    Intel compiler modules can define their family as "compiler".  This prevents
    GCC and Intel compilers being loaded simultaneously.

    This function potentially has side effects on the environment.  When a
    module is loaded, if a module of the same family is already loaded, they
    will be swapped.  Swapping has the potential to change the MODULEPATH and
    state of loaded modules.


**get_family_info**\ *(name, \*\*kwargs)*
    Returns information about family `name`

    If a module of family `name` is loaded, this function returns its name and
    version.  Otherwise, the name and version return as `None`


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Functions for relaying information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**help**\ *(help_string, \*\*kwargs)*
    Sets a help message for `module`


**is_loaded**\ *(name)*
    Report whether the module `name` is loaded


**whatis**\ *(\*args, \*\*kwargs)*
    Sets the "whatis" informational string for `module`


^^^^^^^^^^^^^^^^^^^^^^^^
General module functions
^^^^^^^^^^^^^^^^^^^^^^^^

**load**\ *(name, \*\*kwds)*
    Load the module `name`

    In load mode, loads the module found by `name` if it is not already loaded.
    If it is loaded, its internal reference count is incremented.

    In unload mode, decrements the reference count of the module found by
    `name`.  If the reference count gets to 0, the module is unloaded.


**load_first**\ *(\*names)*
    Load the first of modules in `names`

    In load mode, loads the first available module in `names` and returns it. In
    unload mode, the first loaded module in `names` is unloaded.

    If the last of `names` is None, no error is thrown if no available modules
    are found in `names`


**swap**\ *(cur, new, \*\*kwargs)*
    Swap module `cur` for module `new`

    In load mode, perform an unload of `cur` followed by a load of `new`.
    However, when unloading `cur`, all modules loaded after `cur` are also
    unloaded in reverse order.  After loading `new`, the unloaded modules are
    reloaded in the order they were originally loaded.  If MODULEPATH changes as
    a result of the swap, it is possible that some of these modules will be
    swapped themselves, or not reloaded at all.

    In unload mode, the swap is not performed.


**unload**\ *(name)*
    Unload the module `name`

    In load mode, decrements the reference count of the module found by `name`.
    If the reference count drops to 0, the module is unloaded.

    If the module is not found, or is not loaded, nothing is done.

    In unload mode, nothing is done.


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Functions for defining shell aliases and functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**set_alias**\ *(name, value)*
    Define a shell alias

    In load mode, defines the shell alias.  In unload mode, undefines it.


**set_shell_function**\ *(name, value)*
    Define a shell function

    In load mode, defines the shell function.  In unload mode, undefines it.


**unset_alias**\ *(name)*
    Undefine a shell alias

    In unload mode, nothing is done.  Otherwise, the alias given by `name` is
    undefined.


**unset_shell_function**\ *(name)*
    Undefine a shell function

    In unload mode, nothing is done.  Otherwise, the function given by `name` is
    undefined.

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
