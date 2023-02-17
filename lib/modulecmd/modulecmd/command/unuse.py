import modulecmd.system


description = "Remove (unuse) directory[s] from MODULEPATH"
level = "short"
section = "modulepath"


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
    message with -h."""
    subparser.add_argument("path", help="Path[s] to unuse.")


def unuse(parser, args):
    modulecmd.system.unuse(args.path)
    modulecmd.system.dump()
