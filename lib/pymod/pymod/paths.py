"""Defines paths that are part of pymod's directory structure.

Do not import other ``pymod`` modules here. This module is used
throughout Modulecmd.py and should bring in a minimal number of external
dependencies.
"""
import os
import sys


def ancestor(dir, n=1):
    """Get the nth ancestor of a directory."""
    parent = os.path.abspath(dir)
    for i in range(n):
        parent = os.path.dirname(parent)
    return parent


#: This file lives in $prefix/lib/pymod/pymod/__file__
prefix = ancestor(__file__, 4)

#: synonym for prefix
pymod_root = prefix

#: bin directory in the pymod prefix
bin_path = os.path.join(prefix, "bin")

#: The pymod script itself
pymod_script = os.path.join(bin_path, "pymod")

# pymod directory hierarchy
lib_path = os.path.join(prefix, "lib", "pymod")
external_path = os.path.join(lib_path, "contrib")
module_path = os.path.join(lib_path, "pymod")
command_path = os.path.join(module_path, "command")
callback_path = os.path.join(module_path, "callback")
test_path = os.path.join(module_path, "test")
modulepath_path = os.path.join(module_path, "modulepath")
var_path = os.path.join(prefix, "var", "pymod")
share_path = os.path.join(prefix, "share", "pymod")
docs_path = os.path.join(prefix, "docs", "pymod")
etc_path = os.path.join(prefix, "etc", "pymod")


#: User configuration location
user_config_path = os.getenv("PYMOD_USER_CONFIG_PATH", os.path.expanduser("~/.pymod"))
user_cache_path = os.getenv("PYMOD_USER_CACHE_PATH", os.path.expanduser("~/.pymod/cache"))

if not os.path.isdir(user_config_path):  # pragma: no cover
    os.makedirs(user_config_path)

if not os.path.isdir(user_cache_path):  # pragma: no cover
    os.makedirs(user_cache_path)

def join_user(basename, cache=False):
    if cache:
        return os.path.join(user_cache_path, basename)
    return os.path.join(user_config_path, basename)


del sys
