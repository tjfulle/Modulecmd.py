import pymod.mc

description = "Show path to module file"
level = "short"
section = "info"


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument("names", nargs="+", help="Name of module")


def find(parser, args):
    pymod.mc.find(args.names)
