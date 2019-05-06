import os
import sys
import pymod.modulepath
from pymod.error import ModuleNotFoundError
from contrib.util.logging.pager import pager
from contrib.util.logging.color import colorize
from contrib.util.logging import terminal_size
from pymod.mc.execmodule import execmodule_in_sandbox

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


def display_module_help(name):
    module = pymod.modulepath.get(name)
    if module is None:
        raise ModuleNotFoundError(name, mp=pymod.modulepath)
    execmodule_in_sandbox(module, 'help')
    _, width = terminal_size()
    x = " " + module.name + " "
    s = '{0}'.format(x.center(width, '=')) + '\n'
    s += module.format_help() + '\n'
    s += '=' * width
    stream.write(s + '\n')

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
            display_module_help(args.help_command)
    else:
        sys.stderr.write(parser.format_help(level=args.all))
