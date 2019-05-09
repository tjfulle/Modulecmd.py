import argparse

import pymod.mc
from pymod.command.common import parse_module_options

description = 'Load modules into environment'
level = 'short'
section = 'module'


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument(
        '-i', '--insert-at', type=int, default=None,
        help='Load the module as the `i`th module.')
    subparser.add_argument(
        'args', nargs=argparse.REMAINDER,
        help=('Modules and options to load. Additional options can be sent \n'
              'directly to the module using the syntax, `+option[=value]`. \n'
              'See the module options help for more details.'))


def load(parser, args):
    argv = parse_module_options(args.args)
    for (name, opts) in argv:
        pymod.mc.load(name, opts=opts, insert_at=args.insert_at)
    pymod.mc.dump()
    return 0
