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

    If `name==MODULEPATH`, this function calls `use(value, append=True)` for
    each `value` in `values`.

    A path-like variable stores a list as a `sep` separated string.  eg, the
    PATH environment variable is a `sep` separated list of directories:

        echo $PATH     dirname1:dirname2:...


**prepend_path**\ *(name, \*values, \*\*kwds)*
    Prepend `values` to path-like variable `name`

    In unload mode, `values` are removed from path-like variable `name`,
    otherwise, they are prepended.

    If `name==MODULEPATH`, this function calls `use(value)` for each `value` in
    `values`.

    A path-like variable stores a list as a `sep` separated string.  eg, the
    PATH environment variable is a `sep` separated list of directories:

        echo $PATH     dirname1:dirname2:...


**remove_path**\ *(name, \*values, \*\*kwds)*
    Removes `values` from path-like variable `name`

    In unload mode, nothing is done.  Otherwise, `values` are removed from path-
    like variable `name`.

    If `name==MODULEPATH`, this function calls `unuse(value)` for each `value`
    in `values`.

    A path-like variable stores a list as a `sep` separated string.  eg, the
    PATH environment variable is a `sep` separated list of directories:

        echo $PATH     dirname1:dirname2:...


^^^^^^^^^^^^^^^^^^^^^^^^^
General purpose utilities
^^^^^^^^^^^^^^^^^^^^^^^^^

**check_output**\ *(command)*
    Run command with arguments and return its output as a string.


**colorize**\ *(string, \*\*kwargs)*
    Replace all color expressions in a string with ANSI control codes.


**execute**\ *(command, when=None)*
    Executes the command `command` in a subprocess


**listdir**\ *(dirname, key=None)*
    List contents of directory `dirname`


**mkdirp**\ *(\*paths, \*\*kwargs)*
    Make directory `dir` and all intermediate directories, if necessary.


**source**\ *(filename)*
    Sources a shell script given by filename

    Warning: this function sources a shell script unconditionally.  Environment
    modifications made by the script are not tracked by Modulecmd.py.


**stop**\ *()*
    Stop loading this module


**which**\ *(exename)*
    Return the path to an executable, if found on PATH


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Functions for interacting with other modules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**conflict**\ *(\*names, \*\*kwargs)*
    Defines conflicts (modules that conflict with `module`)

    In load mode, asserts that none of `names` is loaded.   Otherwise, nothing
    is done.


**prereq**\ *(\*names)*
    Defines a prerequisite (module that must be loaded) for this module

    In load mode, asserts that `name` is loaded.  Otherwise, nothing is done.


**prereq_any**\ *(\*names)*
    Defines prerequisites (modules that must be loaded) for this module

    In load mode, asserts that at least one of the modules given by `names` is
    loaded.  In unload mode, nothing is done.


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Functions for interacting with module families
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**family**\ *(family_name, \*\*kwargs)*
    Defines the "family" of the module

    Only one module in a family can be loaded at a time.  For instance, GCC and
    Intel compiler modules can define their family as "compiler".  This prevents
    GCC and Intel compilers being loaded simultaneously.


**get_family_info**\ *(name, \*\*kwargs)*
    Returns information about family `name`


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


**load_first**\ *(\*names)*
    Load the first of modules in `names`

    In load mode, loads the first available module in `names` and returns it. In
    unload mode, the first loaded module in `names` is unloaded.


**swap**\ *(cur, new, \*\*kwargs)*
    Swap module `cur` for module `new`

    In load mode, perform an unload of `cur` followed by a load of `new`.
    However, when unloading `cur`, all modules loaded after `cur` are also
    unloaded in reverse order.  After loading `new`, the unloaded modules are
    reloaded in the order they were originally loaded.  If MODULEPATH changes as
    a result of the swap, it is possible that some of these modules will be
    swapped themselves, or not reloaded at all.


**unload**\ *(name)*
    Unload the module `name`

    In load mode, decrements the reference count of the module found by `name`.
    If the reference count drops to 0, the module is unloaded.

    If the module is not found, or is not loaded, nothing is done.


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Functions for defining shell aliases and functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**set_alias**\ *(name, value)*
    Define a shell alias


**set_shell_function**\ *(name, value)*
    Define a shell function


**unset_alias**\ *(name)*
    Undefine a shell alias


**unset_shell_function**\ *(name)*
    Undefine a shell function


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Functions for modifying the environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**setenv**\ *(name, value)*
    Set value of environment variable `name`


**unsetenv**\ *(name)*
    Unset value of environment variable `name`


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Functions for interacting with the MODULEPATH
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**unuse**\ *(dirname)*
    Remove the directory `dirname` from MODULEPATH

    In load mode, removes `dirname` from MODULEPATH (it it is on MODULEPATH). In
    unload mode, nothing is done.


**use**\ *(dirname, append=False)*
    Add the directory `dirname` to MODULEPATH

    In load mode, add `dirname` to MODULEPATH.  In unload mode, remove `dirname`
    from MODULEPATH (if it is on MODULEPATH).



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
