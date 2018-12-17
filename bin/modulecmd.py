#!/usr/bin/env python
import os
import sys

__this_dir__ = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(__this_dir__, '../lib'))

import pymod

if __name__ == '__main__':

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
