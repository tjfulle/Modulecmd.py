[![codecov](https://codecov.io/gh/tjfulle/Modulecmd.py/branch/master/graph/badge.svg)](https://codecov.io/gh/tjfulle/Modulecmd.py/branch/master)

# Introduction

`Modulecmd.py` is an environment module system inspired by TCL [Environment Modules](http://modules.sourceforge.net) and Lua [lmod](https://lmod.readthedocs.io/en/latest/) and written in Python.  `Modulecmd.py` is compatible with Python 2.7 and 3.5+ and does not require additional compilation.

`Modulecmd.py` provides a Framework for processing module files written in Python.  Additionally, `Modulecmd.py` processes TCL modules by wrapping the TCL module command.  TCL compatibility requires that `tclsh` be found on the user's `PATH` (the TCL module command is provided by `Modulecmd.py`).  Likewise, `lmod` can process most TCL modules.

## Why another module system?

TCL modules and the associated TCL module command are ubiquitous on most HPC systems I work on, but I don't work in/write TCL; `lmod` adds unique capabilities to the TCL module command and is actively developed, but is not available on most of the machines I work on and requires an extra build step; but mostly, I prefer to write python and every system on which I work has a Python installation.

# What Are Environment Modules?

Environment modules, or just modules, are files containing commands that, when processed by the module Framework, modify the current shell's environment.  Modules allow users to dynamically modify their environment.  For example, a module file (call it `foo.py`) containing the following command, sets the environment variable `FOO` to the value `BAR`

```python
setenv('FOO', 'BAR')
```

The module is loaded in to the environment with the following command

```sh
module load foo
```

(note the absence of the extension `.py`).  With modules, environment variables, path-like variables, aliases, and shell functions can be set/unset/modified.

## Why Environment Modules?

Consider the workflow of a developer working on two projects requiring compilers `ucc-1.0` and `ucc-2.0`, respectively.  Binaries created by each compiler are incompatible with the other.  The developer creates two `Modulecmd.py` modules containing the following instructions

`ucc-1.0.py`:

```python
append_path('PATH', '/path/to/ucc-1.0')
```

and 

`ucc-2.0.py`:

```python
append_path('PATH', '/path/to/ucc-2.0')
```

When the developer works on the project requiring `ucc-1.0`, the appropriate module is be loaded, putting the the compiler in the environment's `PATH`.  `ucc-2.0` can later be accessed by unloading module `ucc-1.0` and loading `ucc-2.0`.

This example is meant to merely demonstrate a simplistic usage of `Modulecmd.py` modules.  This document describes the `Modulecmd.py` module Framework in more detail.

## A Note on Terminology

In the context of module files, the term module is different from the standard Python definition.  In Python, a module is a Python file containing python definitions and statements.  Python modules can be imported into other modules.  In contrast, a `Modulecmd.py` environment module, while a python file containing definitions and statements, is not intended to be imported by other Python modules.  Rather, the `Modulecmd.py` module is executed by `Modulecmd.py` using the the `Modulecmd.py` framework.  Commands in a `Modulecmd.py` module are translated and injected in to the user's environment.

# Installation

Clone or download `Modulecmd.py`.  In your `.bashrc`, execute the following:

```
eval `python -B -E ${MODULECMD_PY_DIR}/Contents/Modulecmd/modulecmd.py bash init`
```

where `${MODULECMD_PY_DIR}` is the path to the directory where `Modulecmd.py` is
cloned.

# The module Command

The `Modulecmd.py` initialization defines the `module` shell function that executes `Modulecmd.py` modules.  Valid subcommands of `module` are:

```sh
    reset               Reset environment to initial environment
    setenv              Set environment variables
    avail               Display available modules
    list                Display loaded modules
    edit                Edit module files
    show                Show module[s]
    cat                 cat module[s] to screen
    load                Load module[s]
    unload              Unload module[s]
    reload              Reload module[s]
    use                 Add directory[s] to MODULEPATH
    unuse               Remove directory[s] from MODULEPATH
    purge               Unload all modules
    swap                Swap modules
    whatis              Display module whatis string
```

# Modulecmd.py Module Files

`Modulecmd.py` module files are executed by the `Modulecmd.py` Framework.  `Modulecmd.py` executes module files in an environment providing the following commands:

- `getenv(name)`: Get the value of environment variable given by `name`.  Returns `None` if `name` is not defined. 
- `get_hostname()`: Get the value of the host name of the sytem.
- `mode()`: Return the active mode.  One of `"load"` or `"unload"`

## Message logging

- `log_message(message)`: Log an informational message to the console.
- `log_info(message)`: Log an informational message to the console.
- `log_warning(message)`: Log a warning message to the console.
- `log_error(message)`: Log an error message to the console and quit.

## Environment Modification

- `setenv(variable, value)`: Set the environment variable `variable` to `value`.
- `unsetenv(variable)`: Unset the environment variable `variable`.

- `set_alias(name, value)`: Set the alias `name` to `value`.
- `unset_alias(name)`: Unset the alias given by `name`.

- `set_shell_function(name, value)`: Set the shell function `name` to `value`.
- `unset_shell_function(name, value)`: Unset the shell function `name`

- `prepend_path(pathname, value)`: Prepend `value` to path-like variable `pathname`.
- `append_path(pathname, value)`: Append `value` to path-like variable `pathname`.
- `remove_path(pathname, value)`: Remove `value` from path-like variable `pathname`.

## Interaction with Other Modules

- `prereq(name)`: Module `name` is a prerequisite of this module.  If `name` is not loaded, `Modulecmd.py` will quit.
- `prereq_any(*names)`: Any one of `names` is a prerequisite of this module.  If none of `names` is not loaded, `Modulecmd.py` will quit.

- `load(name)`: Load the module `name`.
- `load_first(*names)`: Load the first module in `names`.
- `unload(name)`: Unload the module `name`.

## Other Commands

- `family(name)`: Set the name of the module's family.
- `execute(command)`: Execute `command` in the current shell.
- `whatis(string)`: Store `string` as an informational message describing this module.

# Other Objects/Constants

- `self`: Reference to this modules object.
- `HOME`: The path to `${HOME}`
- `USER`: The name of `${USER}`
- `IS_DARWIN`: Boolean.  `True` if the system is Darwin.  `False` otherwise.
- `user_env`: Reference to a user defined Python module containing custom commands.
- `args`: List of commands passed from command line to this module.
