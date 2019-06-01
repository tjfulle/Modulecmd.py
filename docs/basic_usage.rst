.. _basic-usage:

===========
Basic Usage
===========


.. _basic-usage-modulepath:

------------------
The ``MODULEPATH``
------------------

Modulecmd.py searches for modules in the user's ``MODULEPATH``.  ``MODULEPATH``
is a colon separated list of directories containing modules.  ``MODULEPATH`` is
to modules what ``PATH`` is to executables.

In the following examples, a mock ``MODULEPATH`` is used.  You can set an
identical mock ``MODULEPATH`` and follow along in your shell by executing

.. code-block:: console

  $ module tutorial basic
  ==> Setting up Modulecmd.py's basic mock tutorial MODULEPATH

This command purges any loaded module and resets the ``MODULEPATH`` to the mock
directories used in this tutorial.  Modulecmd.py can report to you the current
value of ``MODULEPATH`` with the ``path`` subcommand:

.. code-block:: console

  $ module path
  1) ~/Library/Application Support/Modulecmd.py/basic/1
  2) ~/Library/Application Support/Modulecmd.py/basic/2

.. note::

  The exact path displayed may differ from the paths shown depending on
  your operating system.  The final two directories (``basic/1`` and
  ``basic/2``) should be present.


.. _basic-usage-avail:

----------------------
List available modules
----------------------

The subcommand ``avail`` lists available modules:

.. code-block:: console

  $ module avail
  --- ~/Library/Application Support/Modulecmd.py/basic/1 ---
  A  B (D)  C/1.0  C/2.0

  --- ~/Library/Application Support/Modulecmd.py/basic/2 ---
  B  C/1.0  C/3.0 (D)


Several modules are shown as available.  The unversioned modules ``A`` and
``B``, and the versioned module ``C`` with versions ``1.0``, ``2.0``, and
``3.0``, spread across the two directories on ``MODULEPATH``.

Where an unversioned module exists in more than one directory, or a module has
multiple versions, the suffix ``(D)`` indicates its default version.  The
default version is chosen by the following rules:

- If a module is unversioned (such as modules ``A`` and ``B`` above), the first
  module on ``MODULEPATH`` is the default.  In the above example, module ``B``
  in ``~/Library/Application Support/Modulecmd.py/basic/1`` comes before the
  module of the same name in ``~/Library/Application
  Support/Modulecmd.py/basic/2`` and is, thus, the default.

- If a module is versioned (such as module ``C`` above), the highest logical
  version across all directories is chosen as the default.  Accordingly, version
  ``3.0`` of module ``C`` is its default.

.. note::

  There are yet other ways of determining and specifying defaults.  These will
  be covered in the intermediate tutorial.

.. _basic-usage-avail-filtered:

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Filtering list of available modules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The list of available modules can be filtered by regular expression as ``module
avail <regex>``:

.. code-block:: console

  $ module avail C
  --- ~/Library/Application Support/Modulecmd.py/basic/1 ---
  C/1.0  C/2.0

  --- ~/Library/Application Support/Modulecmd.py/basic/2 ---
  C/1.0  C/3.0 (D)

Now, only modules matching the regular expression (``C`` in this case) are
shown.


.. _basic-usage-info:

-------------------------------------
Displaying information about a module
-------------------------------------

Modulecmd.py can report basic information about modules on ``MODULEPATH``.
A modules file path is displayed using the ``find`` subcommand:

.. code-block:: console

  $ module find C
  C/1.0
    ~/Library/Application Support/Modulecmd.py/basic/1/C/1.0.py
  C/2.0
    ~/Library/Application Support/Modulecmd.py/basic/1/C/2.0.py
  C/1.0
    ~/Library/Application Support/Modulecmd.py/basic/2/C/1.0.py
  C/3.0
    ~/Library/Application Support/Modulecmd.py/basic/2/C/3.0.py

Note that the file paths for all of module ``C``\ s versions were displayed.  To
display the file path of a single version, give ``find`` a more qualified name:

.. code-block:: console

  $ module find C/3.0
  C/3.0
    ~/Library/Application Support/Modulecmd.py/basic/2/C/3.0.py

The contents of the module shown with the ``cat`` subcommand:

.. code-block:: console

  $ module cat A
  setenv('A', 'A-1')
  set_alias('ls-a', 'ls -a')

We see that the module ``A`` sets the environment variable ``A`` to the value
``A-1`` and alias ``ls-a`` to ``ls -a``.

The subcommand ``more`` also shows the contents of a module, but pages through
the output, similar to the Linux ``less`` command.

The subcommand ``show`` shows the commands that would be executed by the shell
when the module is loaded:

.. code-block:: console

  $ module show A
  A="A-1";
  export A;
  alias ls-a='ls -a';

.. note::

  The commands shown above are the commands that would be executed by the
  ``bash`` shell.  For other shells, the commands will be different.

The subcommand ``whatis`` displays more detailed information about the module

.. code-block:: console

  $ module whatis A
  ====================================== A =====================================
  Name: A
  Family: None
  Full Name: A
  Filename: ~/Library/Application Support/Modulecmd.py/basic/1/A.py
  ==============================================================================


.. _basic-usage-load:

-----------------------------
Loading and unloading modules
-----------------------------

The subcommand ``load`` loads a module.  When a module is loaded, its commands
are translated and sent to the shell.  To load the module ``A`` do:

.. code-block:: console

  $ module load A

The ``list`` subcommand lists the loaded modules

.. code-block:: console

  $ module list
  Currently loaded modules
      1) A

Note, the module ``A`` is shown as loaded.

Let’s verify that loading ``A`` had an effect on the shell.  We previously
displayed the contents of ``A`` and saw it set the environment variable ``A`` to
``A-1``.  Let's verify this variable was set

.. code-block:: console

  $ echo $A
  A-1

Loading the module ``C`` loads the default version

.. code-block:: console

  $ module load C
  $ module ls
  Currently loaded modules
      1) A  2) C/3.0

(``ls`` is alias for ``list``).  As expected, version ``3.0`` of ``C`` was
loaded.  To Load a specific version, specify the name and version:

.. code-block:: console

  $ module load C/1.0

  The following modules have been updated with a version change:
    1) C/3.0 => C/1.0

The previously loaded version of module ``C`` was unloaded and version ``1.0``
loaded in its place.

.. code-block:: console

  $ module ls
  Currently loaded modules
      1) A  2) C/1.0


Two modules ``C/1.0`` exist on ``MODULEPATH``.  Which one was loaded?  The
subcommand ``info`` gives basic information about a loaded module

.. code-block:: console

  $ module info C

  Module: C/1.0
    Name:         C
    Version:      1.0
    Modulepath:   ~/Library/Application Support/Modulecmd.py/basic/1

As expected, the module loaded was the first on ``MODULEPATH``.


To unload a module, issue the ``unload`` subcommand

.. code-block:: console

  $ module unload C
  $ module ls
  Currently loaded modules
      1) A

.. _basic-usage-reload:

------------------
Reloading a module
------------------

It is sometimes necessary to reload a module.  Issuing ``load`` on an already
loaded module issues the following warning:

.. code-block:: console

  $ module load A
  ==> Warning: A is already loaded, use 'module reload' to reload

The ``reload`` command must be issued to reload an already loaded module:

.. code-block:: console

  $ module reload A

.. _basic-usage-swap:

----------------
Swapping modules
----------------

Two modules are swapped with the ``swap`` subcommand:

.. code-block:: console

  $ module swap A B
  The following modules have been swapped
    1) A => B

.. code-block:: console

  $ module ls

  Currently loaded modules
      1) B

----------------------------
Adding to the ``MODULEPATH``
----------------------------

The ``use`` subcommand adds paths to ``MODULEPATH``.

------------
Getting help
------------

Several methods exist for generating help on the command line:

.. code-block:: console

  $ module -h

will give display basic subcommands of Modulecmd.py.  The subcommand ``help``
displays an extended help:

.. code-block:: console

  $ module help

To get help on a specific subcommand execute

.. code-block:: console

  $ module <subcommand> -h


----------
Conclusion
----------

In this tutorial, we have looked at the basics of environment modules.  In the
intermediate tutorial, we expand on these concepts and introduce other concepts
that are useful for working with your shell's environment.

To reset your shell to the state before starting the tutorial, execute:

.. code-block:: console

  module tutorial teardown
