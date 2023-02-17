import sys
import modulecmd.system


description = "Displays available modules"
level = "short"
section = "basic"


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument(
        "regex",
        nargs="?",
        metavar="regex",
        help='Highlight available modules matching "regex"',
    )
    subparser.add_argument(
        "-t",
        "--terse",
        default=False,
        action="store_true",
        help="Display output in terse format [default: %(default)s]",
    )
    subparser.add_argument(
        "-a",
        default=False,
        action="store_true",
        help="Include available clones and collections [default: %(default)s]",
    )


def avail(parser, args):
    avail = modulecmd.system.avail(terse=args.terse, regex=args.regex, show_all=args.a)
    sys.stderr.write(avail)
