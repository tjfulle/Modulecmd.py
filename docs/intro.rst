
Introduction
============

``Modulecmd.py`` is an environment module system inspired by TCL [`Environment Modules`_] and Lua [lmod_] and written in Python.  ``Modulecmd.py`` is compatible with Python 2.7 and 3.5+ and does not require additional compilation.

``Modulecmd.py`` provides a framework for processing module files written in Python.  Additionally, ``Modulecmd.py`` processes TCL modules by wrapping the TCL module command.  TCL compatibility requires that ``tclsh`` be found on the user's ``PATH`` (the TCL module command is provided by ``Modulecmd.py``).  Likewise, ``lmod`` can process most TCL modules.

Why another module system?
--------------------------

TCL modules and the associated TCL module command are ubiquitous on most HPC systems I work on, but I don't work in/write TCL; ``lmod`` adds unique capabilities to the TCL module command and is actively developed, but is not available on most of the machines I work on and requires an extra build step; but mostly, I prefer to write python and every system on which I work has a Python installation.

What Are Environment Modules?
-----------------------------

Environment modules, or just modules, are files containing commands that, when processed by the module framework, modify the current shell's environment.  Modules allow users to dynamically modify their environment.  For example, a module file (call it ``foo.py``) containing the following command, sets the environment variable ``FOO`` to the value ``BAR``

.. code-block:: python

  setenv('FOO', 'BAR')

The module is loaded in to the environment with the following command

.. code-block:: console

  module load foo

(note the absence of the extension ``.py``).  With modules, environment variables, path-like variables, aliases, and shell functions can be set/unset/modified.

Why Environment Modules?
------------------------

Consider the workflow of a developer working on two projects requiring compilers ``ucc-1.0`` and ``ucc-2.0``, respectively.  Binaries created by each compiler are incompatible with the other.  The developer creates two ``Modulecmd.py`` modules containing the following instructions

.. code-block:: console

  $ cat ucc-1.0.py

  append_path('PATH', '/path/to/ucc-1.0')

and

.. code-block:: console

  $ cat ucc-2.0.py

  append_path('PATH', '/path/to/ucc-2.0')

When the developer works on the project requiring ``ucc-1.0``, the appropriate module is be loaded, putting the the compiler in the environment's ``PATH``.  ``ucc-2.0`` can later be accessed by unloading module ``ucc-1.0`` and loading ``ucc-2.0``.

This example is meant to merely demonstrate a simplistic usage of ``Modulecmd.py`` modules.  This document describes the ``Modulecmd.py`` module framework in more detail.

A Note on Terminology
=====================

In the context of module files, the term module is different from the standard Python definition.  In Python, a module is a Python file containing python definitions and statements.  Python modules can be imported into other modules.  In contrast, a ``Modulecmd.py`` environment module, while a python file containing definitions and statements, is not intended to be imported by other Python modules.  Rather, the ``Modulecmd.py`` module is executed by ``Modulecmd.py`` using the the ``Modulecmd.py`` framework.  Commands in a ``Modulecmd.py`` module are translated and injected in to the user's environment.

Installation
============

Clone or download ``Modulecmd.py``.  In your ``.bashrc``, execute the following:

.. code-block:: shell

  source ${MODULECMD_PY_DIR}/share/pymod/setup-env.sh
  module init -p=${MODULEPATH}

where ``${MODULECMD_PY_DIR}`` is the path to the directory where ``Modulecmd.py`` is
cloned.

The module Command
------------------

The ``Modulecmd.py`` initialization defines the ``module`` shell function that executes ``Modulecmd.py`` modules.  Valid subcommands of ``module`` are:

.. code-block:: console

   modify environment:
     load (add)            Load modules into environment
     unload (rm)           Unload modules from environment
     reload                Reload a loaded module
     swap                  Swaps two modules, effectively unloading the first then loading the second
     purge                 Remove all loaded modules
     refresh               Unload and reload all loaded modules
     avail (av)            Displays available modules
     info                  Provides information on a particular loaded module
     reset                 Reset environment to initial state

   clones:
     clone                 Manipulate cloned environments

   collections:
     save                  Save loaded modules
     restore               Restore saved modules or, optionally, a clone
     remove                Remove saved collection of modules

   informational:
     list (ls)             Display loaded modules
     whatis                Display module whatis string.  The whatis string is a short informational
                           message a module can provide.  If not defined by the module, a default is
                           displayed.
     show                  Show the commands that would be issued by module load
     cat                   Print contents of a module or collection to the console output.
     more                  Print contents of a module or collection to the console output one
                           page at a time.  Allows movement through files similar to shell's `less`
                           program.
     find (which)          Show path to module file

   modulepath:
     path                  Show MODULEPATH
     use                   Add (use) directory[s] to MODULEPATH
     unuse                 Remove (unuse) directory[s] from MODULEPATH

.. _Environment Modules: http://modules.sourceforge.net
.. _lmod: https://lmod.readthedocs.io/en/latest
