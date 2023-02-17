import modulecmd.system

description = (
    "Swaps two modules, effectively unloading the first " "then loading the second"
)
level = "short"
section = "basic"


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument("first", help="Module to unload")
    subparser.add_argument("second", help="Module to load")


def swap(parser, args):
    modulecmd.system.swap(args.first, args.second)
    modulecmd.system.dump()
