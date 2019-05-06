import os
import sys
from contrib.util.logging.pager import pager
from pymod.command.common import get_entity_text

description = (
    'Print contents of `name` to the console output.  `name` can be the name of a\n'
    'module or collection.')
level = 'short'
section = 'module'


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument(
        'name',
        help='Name of module, collection, or config file')


def cat(parser, args):
    pager(get_entity_text(args.name), plain=True)
