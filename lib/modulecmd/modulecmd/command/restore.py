import modulecmd.system

description = "Restore saved modules or, optionally, a clone"
level = "short"
section = "collections"


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
    message with -h."""
    subparser.add_argument(
        "name",
        nargs="?",
        default=modulecmd.names.default_user_collection,
        help="Name of collection or clone to restore",
    )


def restore(parser, args):
    modulecmd.system.restore_collection(args.name)
    modulecmd.system.dump()
