import os
import sys
import pymod.mc

description = 'Restore saved modules'
level = 'short'
section = 'module'


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument(
        'name', nargs='?',
        default=pymod.names.default_user_collection,
        help='Name of collection to restore')


def restore(parser, args):
    pymod.mc.restore(args.name)
