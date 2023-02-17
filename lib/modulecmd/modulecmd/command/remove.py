import modulecmd.system

description = "Remove saved collection of modules"
level = "short"
section = "collections"


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument("name", help="Name of collection to remove")


def remove(parser, args):
    modulecmd.system.remove_collection(args.name)
