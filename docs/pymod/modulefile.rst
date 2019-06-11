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


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Functions for modifying the environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**setenv**\ *(name, value)*

    Set value of environment variable `name`

    **Arguments**

    *name* (str): Name of the environment variable

    *value* (str): Value to set for environment variable `name`


    **Notes**

    In unload mode, the environment variable is unset.  Otherwise, it is set.
    

    **Examples**

    Consider the module ``baz``
    
    .. code-block:: python
    
        setenv('BAZ', 'baz')
    
    On loading ``baz``, the environment variable is set
    
    .. code-block:: console
    
        $ module load baz
        $ echo ${BAZ}
        baz
    
    On unloading ``baz``, the environment variable is unset
    
    .. code-block:: console
    
        $ module ls
        Currently loaded module
            1) baz
    
        $ module unload baz
        $ echo ${BAZ}

**unsetenv**\ *(name)*

    Unset value of environment variable `name`

    **Arguments**

    *name* (str): Name of the environment variable


    **Notes**

    In unload mode, nothing is done
    

    **Examples**

    Consider the module ``baz``
    
    .. code-block:: python
    
        unsetenv("BAZ")
    
    .. code-block:: console
    
        $ echo ${BAZ}
        baz
    
    On loading, the environment variable ``BAZ`` is unset
    
    .. code-block:: console
    
        $ module load baz
        $ echo ${BAZ}


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

    Consider the module ``baz`` that appends `baz` to the path-like environment variable `BAZ`
    
    .. code-block:: python
    
        append_path('BAZ', 'baz')
    
    The environment variable ``BAZ`` is currently
    
    .. code-block:: console
    
        $ echo ${BAZ}
        spam
    
    On loading the module ``baz``, the environment variable ``BAZ`` is updated:
    
    .. code-block:: console
    
        $ module load baz
        $ echo ${BAZ}
        spam:baz

**prepend_path**\ *(name, \*values, \*\*kwds)*

    Prepend `values` to path-like variable `name`

    **Arguments**

    *name* (str): Name of path-like variable

    *values* (tuple of str): The values to prepend to path-like variable `name`


    **Keyword arguments**

    *sep* (str): defines the separator between values in path-like variable `name` (default is os.pathsep)


    **Notes**

    - In *unload* mode, `values` are removed from path-like variable `name`,       otherwise, they are prepended.
    
    - If ``name==MODULEPATH``, this function calls ``use(value)``       for each `value` in `values`.
    
    - A path-like variable stores a list as a ``sep`` separated string.  eg, the       PATH environment variable is a ``sep`` separated list of directories:
    
      .. code-block:: console
    
          $ echo ${PATH}
          dirname1:dirname2:...
    
    Here, ":" is the separator ``sep``.
    

    **Examples**

    Consider the module ``baz`` that prepends `baz` to the path-like environment variable `BAZ`
    
    .. code-block:: python
    
        prepend_path('BAZ', 'baz')
    
    The environment variable ``BAZ`` is currently
    
    .. code-block:: console
    
        $ echo ${BAZ}
        spam
    
    On loading the module ``baz``, the environment variable ``BAZ`` is updated:
    
    .. code-block:: console
    
        $ module load baz
        $ echo ${BAZ}
        baz:spam

**remove_path**\ *(name, \*values, \*\*kwds)*

    Removes `values` from the path-like variable `name`

    **Arguments**

    *name* (str): Name of path-like variable

    *values* (tuple of str): The values to remove from the path-like variable `name`


    **Keyword arguments**

    *sep* (str): defines the separator between values in path-like variable `name` (default is os.pathsep)


    **Notes**

    - In *unload* mode, nothing is done.  Otherwise, `values` are removed from       path-like variable `name`.
    
    - If ``name==MODULEPATH``, this function calls ``unuse(value)``       for each `value` in `values`.
    
    - A path-like variable stores a list as a ``sep`` separated string.  eg, the       PATH environment variable is a ``sep`` separated list of directories:
    
      .. code-block:: console
    
          $ echo ${PATH}
          dirname1:dirname2:...
    
    Here, ":" is the separator ``sep``.
    

    **Examples**

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


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Functions for defining shell aliases and functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**set_alias**\ *(name, value)*

    Define a shell alias

    **Arguments**

    *name* (str): Name of the alias

    *value* (str): Value of the alias


    **Notes**

    In unload mode, undefines the alias.  Otherwise, defines the alias.
    

    **Examples**

    Consider the module ``baz``
    
    .. code-block:: python
    
        set_alias('baz', 'ls -l')
    
    On loading ``baz``, the alias is defined
    
    .. code-block:: console
    
        $ module load baz
        $ alias baz
        alias baz='ls -l'
    
    On unloading ``baz``, the alias is undefined
    
    .. code-block:: console
    
        $ module ls
        Currently loaded module
            1) baz
    
        $ module unload baz
        $ alias baz
        -bash: alias: baz: not found

**set_shell_function**\ *(name, value)*

    Define a shell function

    **Arguments**

    *name* (str): Name of the function

    *value* (str): Value of the function


    **Notes**

    In unload mode, undefines the shell function.  Otherwise, defines the shell function
    

    **Examples**

    Consider the module ``baz``
    
    .. code-block:: python
    
        set_shell_function('baz', 'ls -l $1')
    
    On loading ``baz``, the shell function is defined
    
    .. code-block:: console
    
        $ module load baz
        $ declare -f baz
        baz ()
        {
            ls -l $1
        }
    
    On unloading ``baz``, the shell function is undefined
    
    .. code-block:: console
    
        $ module ls
        Currently loaded module
            1) baz
    
        $ module unload baz
        $ declare -f baz

**unset_alias**\ *(name)*

    Undefine a shell alias

    **Arguments**

    *name* (str): Name of the shell alias


    **Notes**

    In unload mode, nothing is done.  Otherwise, the alias given by `name` is undefined
    

    **Examples**

    Consider the module ``baz``
    
    .. code-block:: python
    
        unset_alias("baz")
    
    .. code-block:: console
    
        $ alias baz
        alias baz='echo "I am a baz!"'
    
    On loading, the alias ``baz`` is undefined
    
    .. code-block:: console
    
        $ module load baz
        $ alias baz
        -bash: alias: baz: not found

**unset_shell_function**\ *(name)*

    Undefine a shell function

    **Arguments**

    *name* (str): Name of the shell function


    **Notes**

    In unload mode, nothing is done.  Otherwise, the function given by `name` is undefined
    

    **Examples**

    Consider the module ``baz``
    
    .. code-block:: python
    
        unset_shell_function("baz")
    
    .. code-block:: console
    
        $ declare -f baz
        baz ()
        {
            echo "I am a baz!"
        }
    
    On loading, the shell function ``baz`` is undefined
    
    .. code-block:: console
    
        $ module load baz
        $ declare -f baz


^^^^^^^^^^^^^^^^^^^^^^^^
General module functions
^^^^^^^^^^^^^^^^^^^^^^^^

**load**\ *(name, \*\*kwds)*

    Load the module `name`

    **Arguments**

    *name* (str): Name of module to load


    **Keyword arguments**

    *opts* (list): Module options


    **Notes**

    - In load mode, loads the module found by `name` if it is not already loaded.             If it is loaded, its internal reference count is incremented.
    
    - In unload mode, decrements the reference count of the module found by             `name`.  If the reference count gets to 0, the module is unloaded.
    

    **Examples**

    Consider the module ``baz``
    
    .. code-block:: python
    
        load('spam', opts=['+x'])
    
    On loading module ``baz``, the module ``spam``, if available, is loaded with options
    ``opts``.
    
    .. code-block:: console
    
        $ module ls
        No loaded modules
    
        $ module load baz
        $ module ls
        Currently loaded modules
            1) eggs +x  2) baz

**load_first**\ *(\*names)*

    Load the first of modules in `names`

    **Arguments**

    *names* (tuple of str): Names of modules to load


    **Returns**

    *loaded* (Module): The loaded module


    **Notes**

    - In load mode, loads the first available module in `names` and returns it. In             unload mode, the first loaded module in `names` is unloaded.
    
    - If no available modules are found in `names`, an error occurs
    
    - If the last of `names` is None, no error is thrown if no available             modules are found in `names`
    

    **Examples**

    Consider the module ``baz``
    
    .. code-block:: python
    
        load_first('spam', 'eggs')
    
    On loading module ``baz``, the first available module of ``spam`` or ``eggs`` is loaded.
    
    .. code-block:: console
    
        $ module ls
        No loaded modules
    
        $ module load baz
        $ module ls
        Currently loaded modules
            1) eggs  2) baz
    
    The module ``eggs`` was loaded because ``spam`` was not available.

**swap**\ *(cur, new, \*\*kwargs)*

    Swap module `cur` for module `new`

    **Arguments**

    *cur* (str): The name of the module to unload

    *new* (str): The name of the module to load in place of `cur`


    **Returns**

    *loaded* (Module): `cur`\ 's module object


    **Notes**

    - In load mode, perform an unload of `cur` followed by a load of `new`.  However,             when unloading `cur`, all modules loaded after `cur` are also unloaded in             reverse order.  After loading `new`, the unloaded modules are reloaded in             the order they were originally loaded.
    
    - If MODULEPATH changes as a result of the swap, it is possible that some of these             modules will be swapped themselves, or not reloaded at all.
    
    - In unload mode, the swap is not performed.
    

    **Examples**

    Consider the module ``baz``
    
    .. code-block:: python
    
        swap('spam', 'eggs')
    
    On loading ``baz``, the module ``spam`` is swapped for ``eggs`` (if it is already loaded)
    
    .. code-block:: console
    
        $ module ls
        Currently loaded modules
            1) spam
    
        $ module load baz
        Currently loaded modules
            1) eggs  2) baz

**unload**\ *(name)*

    Unload the module `name`

    **Arguments**

    *name* (str): Name of the module to unload


    **Notes**

    - In load mode, decrements the reference count of the module found by `name`.             If the reference count drops to 0, the module is unloaded.
    
    - If the module is not found, or is not loaded, nothing is done.
    
    - In unload mode, nothing is done.
    

    **Examples**

    Consider the module ``baz``
    
    .. code-block:: python
    
        unload('spam')
    
    On loading ``baz``, the module ``spam`` is unloaded (if it is already loaded)
    
    .. code-block:: console
    
        $ module ls
        Currently loaded modules
            1) spam
    
        $ module load baz
        Currently loaded modules
            1) baz


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Functions for interacting with other modules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**conflict**\ *(\*names, \*\*kwargs)*

    Defines conflicts (modules that conflict with `module`)

    **Arguments**

    *names* (tuple of str): Names of conflicting modules


    **Notes**

    In load mode, asserts that none of `names` is loaded.   Otherwise, nothing
    is done.

**prereq**\ *(\*names)*

    Defines a prerequisite (module that must be loaded) for this module

    **Arguments**

    *names* (tuple of str): Names of prerequisite modules


    **Notes**

    In load mode, asserts that every `name` in `names` is loaded.  Otherwise, nothing is done.
    

    **Examples**

    Consider the module ``baz``
    
    .. code-block:: python
    
        prereq('spam', 'eggs')
    
    If any ``spam`` or ``eggs`` is not loaded, an error occurs:
    
    .. code-block:: console
    
        $ module ls
        Currently loaded module
            1) spam
    
        $ module load baz
        ==> Error: Prerequisite 'eggs' must first be loaded

**prereq_any**\ *(\*names)*

    Defines prerequisites (modules that must be loaded) for this module

    **Arguments**

    *names* (tuple of str): Names of prerequisite modules


    **Notes**

    In load mode, asserts that at least one of the modules given by `names` is
    loaded.  Otherwise, nothing is done.
    

    **Examples**

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


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Functions for interacting with module families
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**family**\ *(family_name)*

    Defines the "family" of the module

    **Arguments**

    *family_name* (str): Name of the family


    **Notes**

    - Only one module in a family can be loaded at a time.  For instance, GCC and       Intel compiler modules can define their family as "compiler".  This prevents       GCC and Intel compilers being loaded simultaneously.
    
    - This function potentially has side effects on the environment.  When       a module is loaded, if a module of the same family is already loaded, they       will be swapped.  Swapping has the potential to change the ``MODULEPATH`` and       state of loaded modules.
    

    **Examples**

    Consider modules ``ucc`` and ``xcc`` that are both members of the ``compiler`` family.
    The module ``ucc/1.0`` is already loaded
    
    .. code-block:: console
    
        $ module ls
        Currently loaded modules
            1) ucc/1.0
    
    On loading ``xcc/1.0``, ``ucc/1.0`` is unloaded
    
    .. code-block:: console
    
        $ module load xcc/1.0
    
        The following modules in the same family have been updated with a version change:
          1) ucc/1.0 => xcc/1.0 (compiler)

**get_family_info**\ *(name, \*\*kwargs)*

    Returns information about family `name`

    **Arguments**

    *name* (str): The name of the family to get information about


    **Returns**

    *family_name* (str): The module name in family `name`

    *version* (str): The version of the module in family `name`


    **Notes**

    If a module of family `name` is loaded, this function returns its name and
    version.  Otherwise, the name and version return as `None`
    

    **Examples**

    The following module performs actions if the compiler ``ucc`` is loaded
    
    .. code-block:: python
    
        name, version = get_family_info('compiler')
        if name == 'ucc':
            # Do something specific if ucc is loaded


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Functions for interacting with the MODULEPATH
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**unuse**\ *(dirname)*

    Remove the directory `dirname` from ``MODULEPATH``

    **Arguments**

    *dirname* (str): Name of the directory to remove from ``MODULEPATH``


    **Notes**

    In load mode, removes `dirname` from the ``MODULEPATH`` (it it is on the ``MODULEPATH``).
    In unload mode, nothing is done.
    
    This function potentially has side effects on the environment.  When
    a directory is ``unuse``\ d, modules in its path will become unavailable and, if
    loaded, will be unloaded.

**use**\ *(dirname, append=False)*

    Add the directory `dirname` to ``MODULEPATH``

    **Arguments**

    *dirname* (str): Name of the directory to add to ``MODULEPATH``


    **Keyword arguments**

    *append* (bool): Append `dirname` to ``MODULEPATH``, otherwise `dirname` is prepended. The default is ``False``.


    **Notes**

    In load mode, adds `dirname` to the ``MODULEPATH``.  In unload mode, remove
    `dirname` from the ``MODULEPATH`` (if it is on ``MODULEPATH``).
    
    This function potentially has side effects on the environment.  When
    a directory is ``use``\ d, modules in its path may have higher precedence than
    modules on the previous ``MODULEPATH``.  Thus, defaults could change and loaded
    modules could be swapped for newer modules with higher precedence.


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Functions for relaying information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**help**\ *(help_string, \*\*kwargs)*

    Sets a help message for `module`

    **Arguments**

    *help_string* (str): Help message for the module


    **Notes**

    This function sets the help string displayed by
    
    .. code-block:: console
    
        $ module help <name>

**is_loaded**\ *(name)*

    Report whether the module `name` is loaded

    **Arguments**

    *name* (str): Name of the module to report


    **Returns**

    *is_loaded* (bool): Whether the module given by `name` is loaded


    **Examples**

    
    .. code-block:: python
    
        if is_loaded('baz'):
            # Do something if baz is loaded
            ...

**whatis**\ *(\*args, \*\*kwargs)*

    Sets the "whatis" informational string for `module`

    **Arguments**

    *args* (tuple of str): Information about the module


    **Notes**

    - This function sets the information string displayed by
    
    .. code-block:: console
    
        $ module whatis <name>
    
    - Keyword arguments are interpreted as ``{title: description}``
    

    **Examples**

    Consider the module ``baz``:
    
    .. code-block:: python
    
        whatis("A description about the module",
               a_title="A section in the whatis")
    
    .. code-block:: console
    
        $ module whatis baz
        A description about the module
    
        A Title
        A section in the whatis


^^^^^^^^^^^^^^^^^^^^^^^^^
General purpose utilities
^^^^^^^^^^^^^^^^^^^^^^^^^

**check_output**\ *(command)*

    Run command with arguments and return its output as a string.

    **Arguments**

    *command* (str): The command to run


    **Returns**

    *output* (str): The output of `command`


    **Notes**

    This is a wrapper to `contrib.util.check_output`.  Where
    `subprocess.check_output` exists, it is called.  Otherwise, an implementation of
    `subprocess.check_output` is provided.

**colorize**\ *(string, \*\*kwargs)*

    Replace all color expressions in a string with ANSI control codes.

    **Arguments**

    *string* (str): The string to replace


    **Keyword arguments**

    *color* (bool): If False, output will be plain text without control codes, for output to non-console devices.


    **Returns**

    *colorized* (str): The filtered string


    **Notes**

    This is a wrapper to `llnl.util.tty.color.colorize`.

**execute**\ *(command, when=None)*

    Executes the command `command` in a subprocess

    **Arguments**

    *command* (str): The command to execute in a shell subprocess


    **Keyword arguments**

    *when* (bool): Logical describing when to execute `command`. If `None` or `True`, `command` is executed.


    **Examples**

    Consider the module ``baz``:
    
    .. code-block:: python
    
        execute(<command>, when=mode()=='load')
    
    The command ``<command>`` will be executed in a subprocess when the module is loaded.

**listdir**\ *(dirname, key=None)*

    List contents of directory `dirname`

    **Arguments**

    *dirname* (str): Path to directory


    **Keyword arguments**

    *key* (callable): Filter for contents in `dirname`


    **Returns**

    *contents* (list): Contents of `dirname`


    **Notes**

    - This is a wrapper to ``contrib.util.listdir``
    - If ``key`` is given, it must be a callable object

**mkdirp**\ *(\*paths, \*\*kwargs)*

    Make directory and all intermediate directories, if necessary.

    **Arguments**

    *paths* (tuple of str): Paths to create


    **Keyword arguments**

    *mode* (permission bits): optional permissions to set on the created directory -- uses OS default if not provided


    **Notes**

    This is a wrapper to `llnl.util.filesystem.mkdirp`.

**source**\ *(filename)*

    Sources a shell script given by filename

    **Arguments**

    *filename* (str): Name of the filename to source


    **Notes**

    - **Warning:** This function sources a shell script unconditionally.  Environment             modifications made by the script are not tracked by Modulecmd.py.
    
    - `filename` is sourced only if ``mode()=='load'`` and is only sourced once

**stop**\ *()*

    Stop loading this module at this point

    **Notes**

    All commands up to the call to `stop` are executed.
    

    **Examples**

    Consider the module ``baz``
    
    .. code-block:: python
    
        # Actions to perform
        ...
        if condition:
            stop()
    
        # Actions not performed if condition is met

**which**\ *(exename)*

    Return the path to an executable, if found on PATH

    **Arguments**

    *exename* (str): The name of the executable


    **Returns**

    *which* (str): The full path to the executable


    **Notes**

    This is a wrapper to `contib.util.which`.




-------
Logging
-------

**log_info**\ *(message)*

    Writes an informational message to the console.

    **Arguments**

    *message* (str): Message to write

**log_warning**\ *(message)*

    Writes a warning message to the console.

    **Arguments**

    *message* (str): Message to write

**log_error**\ *(message)*

    Writes an error message to the console and raises an exception

    **Arguments**

    *message* (str): Message to write


---------------------
Other defined objects
---------------------

**is_darwin**, **IS_DARWIN**

    Is the OS darwin?

**env**

    A reference to the current environment

**self**

    A reference to the module itself

**user_env**

    A reference to the user's environment file

**getenv**\ *(name)*

    Get an environment variable

    **Arguments**

    *name* (str): The name of the desired environment variable

**get_hostname**\ *()*

    Get the host name

**mode**\ *()*

    The current mode ('load', 'unload', etc)

--------------
Module Options
--------------
A module can support command line options.  Options are specified on the command line as

.. code-block:: console

  $ module load <modulename> [+option[=value] [+option...]]

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

  $ module load spam +b +x=baz

.. _Modulecmd.py: https://www.github.com/tjfulle/Modulecmd.py
