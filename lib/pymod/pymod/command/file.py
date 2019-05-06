import os
import sys
import pymod.modulepath
from pymod.error import ModuleNotFoundError

description = 'Show path to module file'
level = 'short'
section = 'module'


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument('names', nargs='+', help='Name of module')


def file(parser, args):
    for name in args.names:
        module = pymod.modulepath.get(name)
        if module is None:
            raise ModuleNotFoundError(name)
        sys.stderr.write(module.filename + '\n')
