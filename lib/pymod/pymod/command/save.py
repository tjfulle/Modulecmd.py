import os
import sys
import pymod.mc

description = 'Save loaded modules'
level = 'short'
section = 'module'


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument(
        'name', help='Name of collection to save')
    subparser.add_argument(
        '--local', action='store_true', default=False,
        help='Save the collection locally')


def save(parser, args):
    pymod.mc.save(args.name, local=args.local)
