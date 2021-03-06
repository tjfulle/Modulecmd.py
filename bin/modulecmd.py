#!/usr/bin/env python

from __future__ import print_function

import os
import sys

if sys.version_info[:2] < (2, 6):
    v_info = sys.version_info[:3]
    sys.exit("Modulecmd.py requires Python 2.6 or higher."
             "This is Python %d.%d.%d." % v_info)

# Find pymod's location and its prefix.
pymod_file = os.path.realpath(os.path.expanduser(__file__))
pymod_prefix = os.path.dirname(os.path.dirname(pymod_file))

# Allow pymod libs to be imported in our scripts
pymod_lib_path = os.path.join(pymod_prefix, "lib", "pymod")
sys.path.insert(0, pymod_lib_path)

# Add external libs
pymod_external_libs = os.path.join(pymod_lib_path, "external")

if sys.version_info[:2] == (2, 6):
    sys.path.insert(0, os.path.join(pymod_external_libs, 'py26'))

sys.path.insert(0, pymod_external_libs)

# Briefly: ruamel.yaml produces a .pth file when installed with pip that
# makes the site installed package the preferred one, even though sys.path
# is modified to point to another version of ruamel.yaml.
if 'ruamel.yaml' in sys.modules:
    del sys.modules['ruamel.yaml']

if 'ruamel' in sys.modules:
    del sys.modules['ruamel']

# Once we've set up the system path, run the pymod main method
import pymod.main  # noqa
sys.exit(pymod.main.main())
