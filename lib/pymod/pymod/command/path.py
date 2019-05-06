import sys
import pymod.modulepath

description = 'Show MODULEPATH'
level = 'short'
section = 'module'


def setup_parser(subparser):
    pass


def path(parser, args):
    s = '\n'.join('{0}) {1}'.format(i, dirname) for i, dirname
                  in enumerate(pymod.modulepath.path(), start=1))
    sys.stderr.write(s + '\n')
