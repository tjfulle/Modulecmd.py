.. _basic-usage:

===========
Basic Usage
===========

Basic concepts of modules and Modulecmd.py are described by way of example in this tutorial.  You can follow along with the examples by loading this tutorial's environment by executing

.. code-block:: console

  $ module tutorial basic
  ==> Setting up Modulecmd.py's basic mock tutorial MODULEPATH

in your shell.

.. _basic-usage-modulepath:

------------------
The ``MODULEPATH``
------------------

Modulecmd.py searches for modules on the user's ``MODULEPATH``.  The ``MODULEPATH`` environment variable is a colon separated list of directories containing modules.  ``MODULEPATH`` is to modules what ``PATH`` is to executables.

In the following examples, a mock ``MODULEPATH`` is used.  Executing the command ``module tutorial basic`` set a the mock ``MODULEPATH`` in your shell so that you can follow along. This command purged any loaded modules and reset the ``MODULEPATH`` to the mock directories used in this tutorial.  Modulecmd.py can report to you the current value of ``MODULEPATH`` with the ``path`` subcommand:

.. code-block:: console

  $ module path
  1) <tmp-prefix>/<user>/Modulecmd.py/basic/modules/1
  2) <tmp-prefix>/<user>/Modulecmd.py/basic/modules/2

.. note::

  The paths displayed in your shell will from those above because the temporary directory <tmp-prefix> is operating system dependent.  <user> is your user name as reported by Python.

.. _basic-usage-avail:

----------------------
List available modules
----------------------

The subcommand ``avail`` lists available modules:

.. code-block:: console

  $ module avail
  - <tmp-prefix>/<user>/Modulecmd.py/basic/modules/1 -
  A  B (D)  C/1.0

  - <tmp-prefix>/<user>/Modulecmd.py/basic/modules/2 -
  B  C/2.0 (D)

Several modules are shown as available.  The unversioned modules ``A`` and ``B``, and the versioned module ``C`` with versions ``1.0`` and ``2.0`` spread across the two directories on ``MODULEPATH``.

Where an unversioned module exists in more than one directory, or a module has multiple versions, the suffix ``(D)`` indicates its default version.  The default version is chosen by the following rules:

- If a module is unversioned (such as modules ``A`` and ``B`` above), the first module on ``MODULEPATH`` is the default.  In the above example, module ``B`` in ``<tmp-prefix>/<user>/Modulecmd.py/basic/1`` comes before the module of the same name in ``<tmp-prefix>/<user>/Modulecmd.py/basic/2`` and is, thus, the default.

- If a module is versioned (such as module ``C`` above), the highest logical version across all directories is chosen as the default.  Accordingly, version ``2.0`` of module ``C`` is its default.

.. note::

  There are yet other ways of determining and specifying defaults.  These will be covered in the intermediate tutorial.

.. _basic-usage-avail-filtered:

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Filtering the list of available modules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The list of available modules can be filtered by regular expression as ``module avail <regex>``:

.. code-block:: console

  $ module avail C
  - <tmp-prefix>/<user>/Modulecmd.py/basic/modules/1 -
  C/1.0

  - <tmp-prefix>/<user>/Modulecmd.py/basic/modules/2 -
  C/2.0 (D)

Now, only modules matching the regular expression (``C`` in this case) are shown.

.. _basic-usage-info:

-------------------------------------
Displaying information about a module
-------------------------------------

Modulecmd.py can report basic information about modules on ``MODULEPATH``. A modules file path is displayed using the ``find`` subcommand:

.. code-block:: console

  $ module find C
  C/1.0
    <tmp-prefix>/<user>/Modulecmd.py/basic/modules/1/C/1.0.py
  C/2.0
    <tmp-prefix>/<user>/Modulecmd.py/basic/modules/2/C/2.0.py

Note that the file paths for all of module ``C``\ s versions were displayed.  To display the file path of a single version, give ``find`` a more qualified name:

.. code-block:: console

  $ module find C/2.0
  C/2.0
    <tmp-prefix>/<user>/Modulecmd.py/basic/modules/2/C/2.0.py

The contents of the module shown with the ``cat`` subcommand:

.. code-block:: console

  $ module cat A
  # Prepend the PATH environment variable with my bin directory
  prepend_path('PATH', '<tmp-prefix>/<user>/Modulecmd.py/basic/sw/1/A/bin')

We see that the module ``A`` modifies the ``PATH`` and sets an alias.

The subcommand ``more`` also shows the contents of a module, but pages through the output, similar to the Linux ``less`` command.

The subcommand ``show`` shows the commands that would be executed by the shell when the module is loaded:

.. code-block:: console

  $ module show A
  PATH="<tmp-prefix>/<user>/Modulecmd.py/basic/sw/1/A/bin:...";
  export PATH;

.. note::

  The portion of the path ``...`` will be specific to the user's shell.

.. note::

  The commands shown above are the commands that would be executed by the ``bash`` shell.  For other shells, the commands will be different.

The subcommand ``info`` displays more detailed information about the module

.. code-block:: console

  $ module info A
  Module: A
    Name:         A
    Loaded:       False
    Modulepath:   <tmp-prefix>/<user>/Modulecmd.py/basic/modules/1

.. _basic-usage-load:

-----------------------------
Loading and unloading modules
-----------------------------

The subcommand ``load`` loads a module.  When a module is loaded, its commands are translated and sent to the shell.  To load the module ``A`` do:

.. code-block:: console

  $ module load A

The ``list`` subcommand lists the loaded modules

.. code-block:: console

  $ module list
  Currently loaded modules
      1) A

Let’s verify that loading ``A`` had an effect on the shell.  We previously displayed the contents of ``A`` and saw it prepended the ``PATH`` environment variable:

.. code-block:: console

  $ echo $PATH
  <tmp-prefix>/<user>/Modulecmd.py/basic/sw/1/A/bin:...

Loading the module ``C`` loads the default version

.. code-block:: console

  $ module load C
  $ module ls
  Currently loaded modules
      1) A  2) C/2.0

(``ls`` is alias for ``list``).  As expected, version ``2.0`` of ``C`` was loaded.

The module ``C`` also modifies the ``PATH``

.. code-block:: console

  $ echo $PATH
  <tmp-prefix>/<user>/Modulecmd.py/basic/sw/2/C/2.0/bin:<tmp-prefix>/<user>/Modulecmd.py/basic/sw/1/A/bin:...

To Load a specific version, specify the name and version:

.. code-block:: console

  $ module load C/1.0

  The following modules have been updated with a version change:
    1) C/2.0 => C/1.0

.. code-block:: console

  $ module ls
  Currently loaded modules
      1) A  2) C/1.0

.. note::

  Only one module of a name can be loaded at a time.  Thus, the previously loaded version of module ``C`` was unloaded and version ``1.0`` loaded in its place.  The modifications to the environment by ``C/2.0`` were undone and modifications by ``C/1.0`` applied.

The subcommand ``avail`` also reports which modules are loaded:

.. code-block:: console

  $ module avail
  - <tmp-prefix>/<user>/Modulecmd.py/basic/modules/1 -
  A  B (D,L)  C/1.0 (L)

  - <tmp-prefix>/<user>/Modulecmd.py/basic/modules/2 -
  B  C/2.0 (D)

Loaded modules are marked with ``(L)``.

To unload a module, issue the ``unload`` subcommand

.. code-block:: console

  $ module unload C
  $ module ls
  Currently loaded modules
      1) A

Unloading a module undoes modifications to the environment specified by it.

.. _basic-usage-reload:

------------------
Reloading a module
------------------

It is sometimes necessary to reload a module.  Issuing ``load`` on an already loaded module issues the following warning:

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

.. _basic-usage-use:

----------------------------
Adding to the ``MODULEPATH``
----------------------------

The ``use`` subcommand modifies ``MODULEPATH`` by either prepending or appending directories to it.  By default, directories are prepended.  Let's add a new directory to ``MODULEPATH``:


.. code-block:: console

  $ module use <tmp-prefix>/<user>/Modulecmd.py/basic/modules/3

  The following modules have been updated with a MODULEPATH change:
    1) B => B

.. note::

  Be sure to substitute <tmp-prefix>/<user> with the OS generated temporary path and user name.

Module ``B`` on the newly added path had higher precedent then the loaded module ``B``, so Modulecmd.py automatically swapped them.

.. code-block:: console

  $ module avail
  - <tmp-prefix>/<user>/Modulecmd.py/basic/modules/3 -
  B (D,L) C/3.0 (D)

  - <tmp-prefix>/<user>/Modulecmd.py/basic/modules/1 -
  A  B  C/1.0

  - <tmp-prefix>/<user>/Modulecmd.py/basic/modules/2 -
  B  C/2.0

The ``unuse`` subcommand removes a directory from ``MODULEPATH``

.. code-block:: console

  $ module unuse <tmp-prefix>/<user>/Modulecmd.py/basic/modules/1

.. code-block:: console

  module avail
  - <tmp-prefix>/<user>/Modulecmd.py/basic/modules/3 -
  B (D,L) C/3.0 (D)

  - <tmp-prefix>/<user>/Modulecmd.py/basic/modules/2 -
  B  C/2.0

.. warning::

  Do not modify ``MODULEPATH`` outside of ``Modulecmd.py`` (eg, by setting/unsetting the environment variable directly).  Doing so will lead to unexpected behavior in Modulecmd.py.

.. _basic-usage-help:

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
