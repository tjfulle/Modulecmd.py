import modulecmd.system

description = "Provides information on a particular loaded module"
level = "short"
section = "basic"


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
    message with -h."""
    subparser.add_argument(
        "names", nargs="+", help="Name[s] of loaded modules to get information for"
    )


def info(parser, args):
    modulecmd.system.info(args.names)
