from contrib.util.tty.pager import pager
from pymod.command.common import get_entity_text

description = (
    'Print contents of a module or collection to the console output one\n'
    'page at a time.  Allows movement through files similar to shell\'s `less`\n'
    'program.')
level = 'short'
section = 'info'


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument(
        'name',
        help='Name of module, collection, or config file')


def more(parser, args):
    pager(get_entity_text(args.name))
