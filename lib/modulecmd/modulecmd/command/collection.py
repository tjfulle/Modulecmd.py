import sys
import modulecmd.system
import modulecmd.collection

description = "Manipulate collections of modules"
level = "short"
section = "collections"


_subcommands = {}


def add_avail_command(parser):
    def avail(args):
        s = modulecmd.collection.avail(terse=args.terse, regex=args.regex)
        sys.stderr.write(s)

    p = parser.add_parser("avail", help="List available (saved) collections")
    p.add_argument(
        "regex",
        nargs="?",
        metavar="regex",
        help='Highlight available modules matching "regex"',
    )
    p.add_argument(
        "-t",
        "--terse",
        action="store_true",
        default=False,
        help="Display output in terse format [default: %(default)s]",
    )
    _subcommands["avail"] = avail


def add_save_command(parser):
    def save(args):
        return modulecmd.system.save_collection(args.name)

    p = parser.add_parser("save", help="Save the current environment")
    p.add_argument(
        "name",
        nargs="?",
        default=modulecmd.names.default_user_collection,
        help="Name of collection to save",
    )
    _subcommands["save"] = save


def add_add_to_loaded_collection_command(parser):
    def add_to_loaded_collection(args):
        return modulecmd.system.add_to_loaded_collection(args.name)

    p = parser.add_parser("add", help="Add module to currently loaded collection")
    p.add_argument(
        "name",
        default=modulecmd.names.default_user_collection,
        help="Name of module to add to currently loaded collection",
    )
    _subcommands["add"] = add_to_loaded_collection


def add_pop_from_loaded_collection_command(parser):
    def pop_from_loaded_collection(args):
        return modulecmd.system.pop_from_loaded_collection(args.name)

    p = parser.add_parser("pop", help="Pop module from currently loaded collection")
    p.add_argument(
        "name",
        default=modulecmd.names.default_user_collection,
        help="Name of module to pop from currently loaded collection",
    )
    _subcommands["pop"] = pop_from_loaded_collection


def add_show_command(parser):
    def show(args):
        return modulecmd.system.show_collection(args.name)

    p = parser.add_parser(
        "show", help="Show actions that would be taken by restoring the collection"
    )
    p.add_argument(
        "name",
        nargs="?",
        default=modulecmd.names.default_user_collection,
        help="Name of collection to show",
    )
    _subcommands["show"] = show


def add_remove_command(parser):
    def remove(args):
        return modulecmd.system.remove_collection(args.name)

    p = parser.add_parser("remove", help="Remove collection")
    p.add_argument("name", help="Name of collection to remove")
    _subcommands["remove"] = remove


def add_restore_command(parser):
    def restore(args):
        modulecmd.system.restore_collectionstore(args.name)
        modulecmd.system.dump()

    p = parser.add_parser("restore", help="Restore collection")
    p.add_argument(
        "name",
        nargs="?",
        default=modulecmd.names.default_user_collection,
        help="Name of collection to restore",
    )
    _subcommands["restore"] = restore


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    sp = subparser.add_subparsers(metavar="SUBCOMMAND", dest="subcommand")
    add_avail_command(sp)
    add_save_command(sp)
    add_show_command(sp)
    add_remove_command(sp)
    add_restore_command(sp)
    add_add_to_loaded_collection_command(sp)
    add_pop_from_loaded_collection_command(sp)


def collection(parser, args):
    _subcommands[args.subcommand](args)
