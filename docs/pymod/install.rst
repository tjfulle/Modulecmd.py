Installation
============

Clone or download `Modulecmd.py`_ and source the appropriate setup script in your shell's initialization script.

--------------------
Shell Initialization
--------------------

`Modulecmd.py`_ initialization scripts define the ``module`` command that executes `Modulecmd.py`_ modules.  Because of differences between shells, users must ``source`` the appropriate initialization script in their shell's startup script.  The `Modulecmd.py`_ initialization scripts are located in ``${MODULECMD_PY_DIR}/share/pymod``, where ``${MODULECMD_PY_DIR}`` is the path to the directory where `Modulecmd.py`_ was cloned or downloaded.

----
Bash
----

In your ``.bashrc``, add the following:

.. code-block:: console

  $ source ${MODULECMD_PY_DIR}/share/pymod/setup-env.sh

---------------------
Test the installation
---------------------

Test the installation with `Modulecmd.py`_'s subcommand ``test``:

.. code-block:: console

  $ module test

which will report passed and failed tests.  Failed tests are considered a bug, please report them to the `Modulecmd.py`_ developers.

---------------------
Module initialization
---------------------

While not necessary, adding a call to the ``init`` subcommand, just after ``source``\ ing the `Modulecmd.py`_ initialization script in your shell's startup script, will perform some useful initializations:


.. code-block:: console

  $ module init [-p=<MODULEPATH>]

The optional ``-p`` flag is used to set an initial ``MODULEPATH``.  See basic-usage_ for a description of the ``MODULEPATH``.


.. _Modulecmd.py: https://www.github.com/tjfulle/Modulecmd.py
