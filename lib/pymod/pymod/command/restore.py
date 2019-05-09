import os
import sys
import pymod.mc

description = 'Restore saved modules or, optionally, a clone'
level = 'short'
section = 'module'


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument(
        'name', nargs='?',
        default=pymod.names.default_user_collection,
        help='Name of collection or clone to restore')
    subparser.add_argument(
        '-c', '--clone', default=False, action='store_true',
        help='Restore a clone instead of a collection')


def restore(parser, args):
    if args.clone:
        pymod.mc.restore_clone(args.name)
    else:
        pymod.mc.restore(args.name)
    pymod.mc.dump()
