import sys
import modulecmd.system
import modulecmd.command
import modulecmd.modulepath
from modulecmd.util.tty import redirect_stdout

description = "get help on modulecmd and its commands"
section = "help"
level = "short"


def setup_parser(subparser):
    help_cmd_group = subparser.add_mutually_exclusive_group()
    help_cmd_group.add_argument(
        "help_command", nargs="?", default=None, help="command or module to get help on"
    )

    help_all_group = subparser.add_mutually_exclusive_group()
    help_all_group.add_argument(
        "-a",
        "--all",
        action="store_const",
        const="long",
        default="short",
        help="print all available commands",
    )


def help(parser, args):

    if args.help_command:
        if args.help_command in modulecmd.command.all_commands():  # pragma: no cover
            parser.add_command(args.help_command)
            with redirect_stdout():
                parser.parse_args([args.help_command, "-h"])
        else:
            with redirect_stdout():
                s = modulecmd.system.help(args.help_command)
                sys.stderr.write(s)

    else:
        with redirect_stdout():
            sys.stderr.write(parser.format_help(level=args.all))
