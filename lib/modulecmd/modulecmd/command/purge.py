import modulecmd.system


description = "Remove all loaded modules"
level = "short"
section = "basic"


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
    message with -h."""
    subparser.add_argument(
        "-F",
        default=None,
        action="store_true",
        help="Do not load modules in `load_after_purge` configuration",
    )


def purge(parser, args):
    modulecmd.system.purge(load_after_purge=not args.F)
    modulecmd.system.dump()
