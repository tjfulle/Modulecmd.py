#!/usr/bin/env python3

from __future__ import print_function

import os
import sys

if sys.version_info[:2] < (2, 6):
    v_info = sys.version_info[:3]
    sys.exit("Modulecmd.py requires Python 2.6 or higher."
             "This is Python %d.%d.%d." % v_info)

# Find modulecmd's location and its prefix.
modulecmd_file = os.path.realpath(os.path.expanduser(__file__))
modulecmd_prefix = os.path.dirname(os.path.dirname(modulecmd_file))

# Allow modulecmd libs to be imported in our scripts
modulecmd_lib_path = os.path.join(modulecmd_prefix, "lib", "modulecmd")
sys.path.insert(0, modulecmd_lib_path)

# Add external libs
modulecmd_external_libs = os.path.join(modulecmd_lib_path, "external")

if sys.version_info[:2] == (2, 6):
    sys.path.insert(0, os.path.join(modulecmd_external_libs, 'py26'))

sys.path.insert(0, modulecmd_external_libs)

# Briefly: ruamel.yaml produces a .pth file when installed with pip that
# makes the site installed package the preferred one, even though sys.path
# is modified to point to another version of ruamel.yaml.
if 'ruamel.yaml' in sys.modules:
    del sys.modules['ruamel.yaml']

if 'ruamel' in sys.modules:
    del sys.modules['ruamel']

# Once we've set up the system path, run the modulecmd main method
import modulecmd.main  # noqa
sys.exit(modulecmd.main.main())
