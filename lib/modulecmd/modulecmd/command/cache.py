import modulecmd.cache

description = "Cache modules"
level = "short"
section = "basic"


_subcommands = {}


def add_build_command(parser):
    def build(args):
        modulecmd.cache.build()

    parser.add_parser("build", help="Build the module cache")
    _subcommands["build"] = build


def add_rebuild_command(parser):
    def rebuild(args):
        modulecmd.cache.remove()
        modulecmd.cache.build()

    parser.add_parser("rebuild", help="Rebuild the module cache")
    _subcommands["rebuild"] = rebuild


def add_remove_command(parser):
    def remove(args):
        modulecmd.cache.remove()

    parser.add_parser("remove", help="Remove the module cache")
    _subcommands["remove"] = remove


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    sp = subparser.add_subparsers(metavar="SUBCOMMAND", dest="subcommand")
    add_build_command(sp)
    add_remove_command(sp)
    add_rebuild_command(sp)


def cache(parser, args):
    _subcommands[args.subcommand](args)
