#!/opt/python/3.9/bin/python3

import os
import sys

if sys.version_info[:3] < (3, 6):
    v_info = sys.version_info[:3]
    sys.exit("Modulecmd.py requires Python 3.6 or higher."
             "This is Python %d.%d.%d." % v_info)

# Find modulecmd's location and its prefix.
modulecmd_file = os.path.realpath(os.path.expanduser(__file__))
modulecmd_prefix = os.path.dirname(os.path.dirname(modulecmd_file))

# Allow modulecmd libs to be imported in our scripts
modulecmd_lib_path = os.path.join(modulecmd_prefix)
sys.path.insert(0, modulecmd_lib_path)

# Once we've set up the system path, run the modulecmd main method
import modulecmd.main  # noqa
sys.exit(modulecmd.main.main())
