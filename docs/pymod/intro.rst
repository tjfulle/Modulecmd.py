============
Introduction
============

Modules provide a method for dynamically changing your shell's environment.  With modules, setting or unsetting environment variables, or creating aliases, for example, is simply a matter of loading an appropriate "module".  Consider the following module:

.. code-block:: console

  $ cat baz.py

  setenv('BAZ', 'SPAM')

On loading the module with

.. code-block:: console

  $ module load baz

(note the absence of the extension ``.py``) the environment variable ``BAZ`` will be set to ``SPAM``:

.. code-block:: console

  $ echo $BAZ
  SPAM

Unloading the module unsets the environment variable

.. code-block:: console

  $ module unload baz
  $ echo $BAZ

``Modulecmd.py`` is an environment module system inspired by TCL [`Environment Modules`_] and Lua [lmod_] and written in Python.  ``Modulecmd.py`` is compatible with Python 2.7 and 3.5+ and does not require additional compilation. ``Modulecmd.py`` provides a framework for processing module files written in Python.  Additionally, ``Modulecmd.py`` processes TCL modules by wrapping the TCL module command.  TCL compatibility requires that ``tclsh`` be found on the user's ``PATH`` (the TCL module command is provided by ``Modulecmd.py``).  Likewise, ``lmod`` can process most TCL modules.

In this guide, basic workflows using ``Modulecmd.py`` are described.  Additionally, instructions for writing module files are provided.

Why another module system?
--------------------------

TCL modules and the associated TCL module command are ubiquitous on most HPC systems I work on, but I don't work in/write TCL; ``lmod`` adds unique capabilities to the TCL module command and is actively developed, but is not available on most of the machines I work on and requires an extra build step; but mostly, I prefer to write python and every system on which I work has a Python installation.

Why Environment Modules?
------------------------

Consider the workflow of a developer working on two projects requiring compilers ``gcc 7`` and ``intel 2017``, respectively.  Binaries created by each compiler are incompatible with the other.  The developer creates two ``Modulecmd.py`` modules containing the following instructions

.. code-block:: console

  $ cat gcc-7.py

  append_path('PATH', '/path/to/gcc-7')

and

.. code-block:: console

  $ cat intel-2017.py

  append_path('PATH', '/path/to/intel-2017')

When the developer works on the project requiring ``gcc 7``, the appropriate module is be loaded, putting the the compiler in the environment's ``PATH``.  ``intel 2017`` can later be accessed by unloading module ``gcc 7`` and loading ``intel 2017``.

This example is meant to merely demonstrate a simplistic usage of ``Modulecmd.py`` modules.  This document describes the ``Modulecmd.py`` module framework in more detail.

A Note on Terminology
=====================

In the context of module files, the term module is different from the standard Python definition.  In Python, a module is a Python file containing python definitions and statements.  Python modules can be imported into other modules.  In contrast, a ``Modulecmd.py`` environment module, while a python file containing definitions and statements, is not intended to be imported by other Python modules.  Rather, the ``Modulecmd.py`` module is executed by ``Modulecmd.py`` using the the ``Modulecmd.py`` framework.  Commands in a ``Modulecmd.py`` module are translated and injected in to the user's environment.

.. _Environment Modules: http://modules.sourceforge.net
.. _lmod: https://lmod.readthedocs.io/en/latest
