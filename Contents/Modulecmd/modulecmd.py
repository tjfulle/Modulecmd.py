#!/usr/bin/env python
from __future__ import division, print_function
import os
import sys
import time
import atexit
import argparse

__this_dir__ = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(__this_dir__, '../Resources/Python'))

import pymod

if __name__ == '__main__':

    if 'cache-system-modules' in sys.argv:
        assert len(sys.argv) == 3
        assert sys.argv.index('cache-system-modules') == 2
        sys.argv[2] = SAVE
        sys.argv.append(DEFAULT_SYS_COLLECTION_NAME)

    if '--profile' in sys.argv:
        sys.argv.remove('--profile')
        try:
            import cProfile as profile
        except ImportError:
            import profile
        output_file = os.path.join(os.getcwd(), 'modulecmd.stats')
        profile.run('pymod.main()', output_file)
    else:
        sys.exit(pymod.main())
