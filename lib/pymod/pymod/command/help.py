import os
import sys
from contrib.util.logging.color import colorize
from contrib.util.logging.pager import pager

description = "get help on pymod and its commands"
section = "help"
level = "short"


def setup_parser(subparser):
    help_cmd_group = subparser.add_mutually_exclusive_group()
    help_cmd_group.add_argument('help_command', nargs='?', default=None,
                                help='command to get help on')

    help_all_group = subparser.add_mutually_exclusive_group()
    help_all_group.add_argument(
        '-a', '--all', action='store_const', const='long', default='short',
        help='print all available commands')

    help_spec_group = subparser.add_mutually_exclusive_group()
    help_spec_group.add_argument(
        '--guide', action='store_const', dest='guide', const='modulefile',
        default=None, help='print guide')


def help(parser, args):
    if args.guide:
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'guides', args.guide + '.txt')
        pager(colorize(open(filename, 'r').read()))
        return 0

    if args.help_command:
        parser.add_command(args.help_command)
        parser.parse_args([args.help_command, '-h'])
    else:
        sys.stderr.write(parser.format_help(level=args.all))
