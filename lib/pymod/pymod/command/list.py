import sys
import pymod.mc

description = "Display loaded modules"
level = "short"
section = "info"


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument(
        "regex", nargs="?", help="Regular expression to highlight in the output"
    )
    subparser.add_argument(
        "-t",
        "--terse",
        default=False,
        action="store_true",
        help="Display output in terse format",
    )
    subparser.add_argument(
        "-c",
        "--show-command",
        default=False,
        action="store_true",
        help="Display commands to load necessary to load the loaded modules",
    )


def list(parser, args):
    s = pymod.mc.list(
        terse=args.terse, show_command=args.show_command, regex=args.regex
    )
    sys.stderr.write(s)
