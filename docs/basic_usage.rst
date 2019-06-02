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
  1) /var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/modules/1
  2) /var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/modules/2

.. note::

  The exact path displayed will differ from the paths shown depending on
  your operating system.  The last four directories in each path
  (``Modulecmd.py/basic/modules/1`` and ``Modulecmd.py/basic/modules/2``) should
  be present.

.. _basic-usage-avail:

----------------------
List available modules
----------------------

The subcommand ``avail`` lists available modules:

.. code-block:: console

  $ module avail
  - /var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/modules/1 -
  A  B (D)  C/1.0

  - /var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/modules/2 -
  B  C/2.0 (D)

Several modules are shown as available.  The unversioned modules ``A`` and
``B``, and the versioned module ``C`` with versions ``1.0`` and ``2.0``
spread across the two directories on ``MODULEPATH``.

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
  ``2.0`` of module ``C`` is its default.

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
  - /var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/modules/1 -
  C/1.0

  - /var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/modules/2 -
  C/2.0 (D)

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
    /var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/modules/1/C/1.0.py
  C/2.0
    /var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/modules/2/C/2.0.py

Note that the file paths for all of module ``C``\ s versions were displayed.  To
display the file path of a single version, give ``find`` a more qualified name:

.. code-block:: console

  $ module find C/2.0
  C/2.0
    /var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/modules/2/C/2.0.py

The contents of the module shown with the ``cat`` subcommand:

.. code-block:: console

  $ module cat A
  whatis("Module A")

  # Prepend the PATH environment variable with my bin directory
  prepend_path('PATH', '/var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/sw/1/A/bin')

  # Set an alias to my script
  set_alias('s-A', '/var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/sw/1/A/bin/A')

We see that the module ``A`` modifies the ``PATH`` and sets an alias.

The subcommand ``more`` also shows the contents of a module, but pages through
the output, similar to the Linux ``less`` command.

The subcommand ``show`` shows the commands that would be executed by the shell
when the module is loaded:

.. code-block:: console

  $ module show A
  PATH="/var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/sw/1/A/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin";
  export PATH;
  alias s-A='/var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/sw/1/A/bin/A';

.. note::

  The commands shown above are the commands that would be executed by the
  ``bash`` shell.  For other shells, the commands will be different.

The subcommand ``whatis`` displays more detailed information about the module

.. code-block:: console

  $ module whatis A
  =========================================== A ===========================================
  Name: A
  Filename: /var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/modules/1/A.py
  =========================================================================================

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
displayed the contents of ``A`` and saw it prepended the ``PATH`` environment
variable:

.. code-block:: console

  $ echo $PATH
  /var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/sw/1/A/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin

Loading the module ``C`` loads the default version

.. code-block:: console

  $ module load C
  $ module ls
  Currently loaded modules
      1) A  2) C/2.0

(``ls`` is alias for ``list``).  As expected, version ``2.0`` of ``C`` was
loaded.

The module ``C`` also modifies the ``PATH``

.. code-block:: console

  $ echo $PATH
  /var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/sw/2/C/2.0/bin:/var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/sw/1/A/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin

To Load a specific version, specify the name and version:

.. code-block:: console

  $ module load C/1.0

  The following modules have been updated with a version change:
    1) C/2.0 => C/1.0

.. code-block:: console

  $ module ls
  Currently loaded modules
      1) A  2) C/1.0

The previously loaded version of module ``C`` was unloaded and version ``1.0``
loaded in its place.  The modifications to the environment by ``C/2.0`` were
undone and modifications by ``C/1.0`` applied:

.. code-block:: console

  $ echo $PATH
  /var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/sw/1/C/1.0/bin:/var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/sw/1/A/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin

To get information about a loaded module, use the subcommand ``info``:

.. code-block:: console

  $ module info C
  Module: C/1.0
    Name:         C
    Version:      1.0
    Modulepath:   /var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/modules/1

The subcommand ``avail`` also reports loaded modules:

.. code-block:: console

  $ module avail
  - /var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/modules/1 -
  A  B (D,L)  C/1.0 (L)

  - /var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/modules/2 -
  B  C/2.0 (D)

The loaded modules are marked with ``(L)``.

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

.. _basic-usage-use:

----------------------------
Adding to the ``MODULEPATH``
----------------------------

The ``use`` subcommand modifies ``MODULEPATH`` by either prepending or appending
directories to it.  By default, directories are prepended.  Let's add a new
directory to ``MODULEPATH``


.. code-block:: console

  $ module use /var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/modules/3

  The following modules have been updated with a MODULEPATH change:
    1) B => B

Module ``B`` on the newly added path had higher precedent then the loaded module ``B``, so Modulecmd.py automatically swapped them.

.. note::

  The path may be slightly different dependent on your operating system.
  Whatever the operating system, the directory you will ``use`` ends in
  ``Modulecmd.py/basic/modules/3``.

.. code-block:: console

  $ module avail
  - /var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/modules/3 -
  B (D,L) C/3.0 (D)

  - /var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/modules/1 -
  A  B  C/1.0 (L)

  - /var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/modules/2 -
  B  C/2.0

Since the new directory contained a logically higher version of module ``C``,
its default changed and is now ``C/3.0``.  Note, however, unlike module ``B``,
Modulecmd.py did not automatically swap module ``C/1.0`` and ``C/3.0`` because
``C/1.0`` was loaded using ``C/1.0``\ 's name and version.

The ``unuse`` subcommand removes a directory from ``MODULEPATH``

.. code-block:: console

  $ module unuse /var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/modules/1

  The following modules have been updated with a MODULEPATH change:
    1) C/1.0 => C/3.0

Loaded module ``C/1.0`` on the path we just unused was updated to the next available
version of ``C/3.0``, as seen below

.. code-block:: console


  module avail
  - /var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/modules/3 -
  B (D,L) C/3.0 (D,L)

  - /var/folders/9t/4fqtb2vs73jd1lbtjb5m4v1m002336/T/tjfulle/Modulecmd.py/basic/modules/2 -
  B  C/2.0

.. warning::

  Do not modify ``MODULEPATH`` outside of ``Modulecmd.py`` (eg, by
  setting/unsetting the environment variable directly).  Doing so will lead to
  unexpected behavior in Modulecmd.py.

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
