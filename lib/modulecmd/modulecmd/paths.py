"""Defines paths that are part of modulecmd's directory structure.

Do not import other ``modulecmd`` modules here. This module is used
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


#: This file lives in $prefix/lib/modulecmd/modulecmd/__file__
prefix = ancestor(__file__, 4)

#: synonym for prefix
modulecmd_root = prefix

#: bin directory in the modulecmd prefix
bin_path = os.path.join(prefix, "bin")

#: The modulecmd script itself
modulecmd_script = os.path.join(bin_path, "modulecmd")

# modulecmd directory hierarchy
lib_path = os.path.join(prefix, "lib", "modulecmd")
external_path = os.path.join(lib_path, "contrib")
module_path = os.path.join(lib_path, "modulecmd")
command_path = os.path.join(module_path, "command")
callback_path = os.path.join(module_path, "callback")
test_path = os.path.join(prefix, "tests")
modulepath_path = os.path.join(module_path, "modulepath")
var_path = os.path.join(prefix, "var", "modulecmd")
share_path = os.path.join(prefix, "share", "modulecmd")
docs_path = os.path.join(prefix, "docs", "modulecmd")
etc_path = os.path.join(prefix, "etc", "modulecmd")


#: User configuration location
user_config_path = os.getenv("PYMOD_USER_CONFIG_PATH", os.path.expanduser("~/.modulecmd"))
user_cache_path = os.getenv("PYMOD_USER_CACHE_PATH", os.path.expanduser("~/.modulecmd/cache"))

if not os.path.isdir(user_config_path):  # pragma: no cover
    os.makedirs(user_config_path)

if not os.path.isdir(user_cache_path):  # pragma: no cover
    os.makedirs(user_cache_path)

def join_user(basename, cache=False):
    if cache:
        return os.path.join(user_cache_path, basename)
    return os.path.join(user_config_path, basename)


del sys
