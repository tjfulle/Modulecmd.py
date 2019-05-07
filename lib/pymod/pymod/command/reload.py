import argparse

import pymod.mc
from pymod.command.common import parse_module_options

description = 'Reload a loaded module'
level = 'short'
section = 'module'


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument('name', help='Module to reload')


def reload(parser, args):
    pymod.mc.reload(args.name)
    pymod.mc.dump()
    return 0