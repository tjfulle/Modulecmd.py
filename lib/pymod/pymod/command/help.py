import os
import sys
import pymod.mc
import pymod.modulepath
from pymod.error import ModuleNotFoundError
from contrib.util.tty.pager import pager
from llnl.util.tty.color import colorize
from llnl.util.tty import terminal_size

description = "get help on pymod and its commands"
section = "help"
level = "short"


def setup_parser(subparser):
    help_cmd_group = subparser.add_mutually_exclusive_group()
    help_cmd_group.add_argument('help_command', nargs='?', default=None,
                                help='command or module to get help on')

    help_all_group = subparser.add_mutually_exclusive_group()
    help_all_group.add_argument(
        '-a', '--all', action='store_const', const='long', default='short',
        help='print all available commands')

    help_spec_group = subparser.add_mutually_exclusive_group()
    help_spec_group.add_argument(
        '--guide', action='store_const', dest='guide', const='modulefile',
        default=None, help='print guide')


def help(parser, args):
    import pymod.command
    if args.guide:
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'guides', args.guide + '.txt')
        pager(colorize(open(filename, 'r').read()))
        return 0

    if args.help_command:
        if args.help_command in pymod.command.all_commands():
            parser.add_command(args.help_command)
            parser.parse_args([args.help_command, '-h'])
        else:
            pymod.mc.help(args.help_command)
    else:
        sys.stderr.write(parser.format_help(level=args.all))
