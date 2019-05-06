import os
import sys
from contrib.util.logging.pager import pager
from pymod.command.common import get_entity_text

description = (
    'print `name` to the console output on page at a time.  Allows movement\n'
    'through files similar to shell\'s `less` program.  `name` can be the name\n'
    'of a module, collection, or configuration file')
level = 'short'
section = 'module'


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument(
        'name',
        help='Name of module, collection, or config file')


def more(parser, args):
    pager(get_entity_text(args.name))
