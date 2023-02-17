# File adapted from spack/cmd/__init__.py

from __future__ import print_function

import os
import re

from llnl.util.lang import attr_setdefault
import llnl.util.tty as tty

import modulecmd.config
import modulecmd.paths


# command has a submodule called "list" so preserve the python list module
python_list = list

# Patterns to ignore in the commands directory when looking for commands.
ignore_files = r"^\.|^__init__.py$|^#|flycheck_"

SETUP_PARSER = "setup_parser"
DESCRIPTION = "description"


def python_name(cmd_name):
    """Convert ``-`` to ``_`` in command name, to make a valid identifier."""
    return cmd_name.replace("-", "_")


def cmd_name(python_name):
    """Convert module name (with ``_``) to command name (with ``-``)."""
    return python_name.replace("_", "-")


#: global, cached list of all commands -- access through all_commands()
_all_commands = None


def all_commands():
    """Get a sorted list of all modulecmd commands.

    This will list the lib/modulecmd/modulecmd/command directory and find the
    commands there to construct the list.  It does not actually import
    the python files -- just gets the names.
    """
    global _all_commands
    if _all_commands is None:
        _all_commands = []
        command_paths = [modulecmd.paths.command_path]  # Built-in commands
        for path in command_paths:
            for file in os.listdir(path):
                if file.endswith(".py") and not re.search(ignore_files, file):
                    command = re.sub(r".py$", "", file)
                    _all_commands.append(cmd_name(command))

        _all_commands.sort()

    return _all_commands


def get_module(cmd_name):
    """Imports the module for a particular command name and returns it.

    Parameters
    ----------
    cmd_name : str
        name of the command for which to get a module (contains ``-``, not ``_``).
    """
    pname = python_name(cmd_name)

    # Import the command from the built-in directory
    module_name = "{0}.{1}".format(__name__, pname)
    module = __import__(
        module_name, fromlist=[pname, SETUP_PARSER, DESCRIPTION], level=0
    )
    tty.debug("Imported {0} from built-in commands".format(pname))

    attr_setdefault(module, SETUP_PARSER, lambda *args: None)  # null-op
    attr_setdefault(module, DESCRIPTION, "")

    if not hasattr(module, pname):  # pragma: no cover
        tty.die(
            "Command module {0} ({1}) must define function {2!r}.".format(
                module.__name__, module.__file__, pname
            )
        )

    return module


def get_command(cmd_name):
    """Imports the command's function from a module and returns it.

    Args:
        cmd_name (str): name of the command for which to get a module
            (contains ``-``, not ``_``).
    """
    pname = python_name(cmd_name)
    return getattr(get_module(pname), pname)
