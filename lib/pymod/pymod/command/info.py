import pymod.mc

description = "Provides information on a particular loaded module"
level = "short"
section = "basic"


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument(
        "names", nargs="+", help="Name[s] of loaded modules to get information for"
    )


def info(parser, args):
    pymod.mc.info(args.names)
