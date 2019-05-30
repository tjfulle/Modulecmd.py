===========
Modulefiles
===========

``Modulecmd.py`` module files are python files that are executed by the ``Modulecmd.py`` Framework.  Modulefiles must have a ``.py`` file extension and must be on the ``MODULEPATH`` to be recognized.  ``Modulecmd.py`` executes module files in an environment providing the following commands:


---------------
General Purpose
---------------

``getenv(name)``
    Get the value of environment variable given by name.  Returns ``None`` if ``name`` is not defined.

``get_hostname()``
    Get the value of the host name of the system.

``mode()``
    Return the active mode.  One of ``"load"`` or ``"unload"``

``self``
    Reference to this modules object.

``HOME``
    The path to HOME

``USER``
    The name of USER

``IS_DARWIN``
    Boolean.  ``True`` if the system is Darwin.  ``False`` otherwise.

``user_env``
    Reference to a user defined Python module containing custom commands.

``args``
    List of commands passed from command line to this module.


---------------
Message Logging
---------------

``log_info(message)``
    Log an informational message to the console.

``log_warning(message)``
    Log a warning message to the console.

``log_error(message)``
    Log an error message to the console and quit.


------------------------
Environment Modification
------------------------

``setenv(name, value)``
    Set the environment variable ``name`` to ``value``.

``unsetenv(name)``
    Unset the environment variable ``name``.

``set_alias(name, value)``
    Set the alias name to ``value``.

``unset_alias(name)``
    Unset the alias given by name.

``set_shell_function(name, value)``
    Set the shell function name to ``value``.

``unset_shell_function(name)``
    Unset the shell function name

``prepend_path(name, value)``
    Prepend ``value`` to path-like variable ``name``.

``append_path(name, value)``
    Append ``value`` to path-like variable ``name``.

``remove_path(name, value)``
    Remove ``value`` from path-like variable ``name``.


------------------------------
Interaction with Other Modules
------------------------------

``prereq(name)``
    Module ``name`` is a prerequisite of this module.  If ``name`` is not loaded, ``Modulecmd.py`` will quit.

``prereq_any(*names)``
    Any one of ``names`` is a prerequisite of this module.  If none of ``names`` is not loaded, ``Modulecmd.py`` will quit.

``conflict(*names)``
    Any of ``names`` conflicts with this module.  If any of ``names`` is loaded, ``Modulecmd.py`` will quit.

``load(name)``
    Load the module ``name``.

``load_first(*names)``
    Load the first module in ``names``.

``unload(name)``
    Unload the module ``name``.


==============
Module Options
==============
A module can support command line options.  Options are specified on the command line as

.. code-block:: console

  module load <modulename> [+option[=value] [+option...]]

The following modulefile functions register options

``add_option(name, action='store_true')``
    Register a module option.  By default, options are boolean flags.  Pass ``action='store'`` to register an option that takes a value.

``parse_opts()``
    Parse module options.  Only options added before calling ``parse_opts`` will be parsed.


--------
Examples
--------

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

==============
Other Commands
==============

``family(name)``
    Set the name of the module's family.

``execute(command)``
    Execute command in the current shell.

``whatis(string)``
    Store string as an informational message describing this module.


========
Examples
========

The following commands, when put in a module file on ``MODULEPATH``, prepends the user's bin directory to the ``PATH`` and aliases the ``ls`` command.

.. code-block:: python

  prepend_path('PATH', '~/bin')
  set_alias('ls', 'ls -lF')
