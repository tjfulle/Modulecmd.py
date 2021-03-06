import pymod.mc

description = "Restore saved modules or, optionally, a clone"
level = "short"
section = "collections"


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument(
        "name",
        nargs="?",
        default=pymod.names.default_user_collection,
        help="Name of collection or clone to restore",
    )


def restore(parser, args):
    pymod.mc.collection.restore(args.name)
    pymod.mc.dump()
