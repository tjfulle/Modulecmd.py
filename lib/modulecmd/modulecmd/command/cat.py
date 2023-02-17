import modulecmd.system

description = "Print contents of a module or collection to the console output."
level = "short"
section = "info"


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument("name", help="Name of module, collection, or config file")


def cat(parser, args):
    modulecmd.system.cat(args.name)
