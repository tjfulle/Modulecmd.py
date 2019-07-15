import pymod.cache

description = 'Cache modules'
level = 'short'
section = 'basic'


_subcommands = {}


def add_build_command(parser):
    def build(args):
        pymod.cache.build()
    p = parser.add_parser('build', help='Build the module cache')
    _subcommands['build'] = build


def add_remove_command(parser):
    def remove(args):
        pymod.cache.remove()
    p = parser.add_parser('remove', help='Remove the module cache')
    _subcommands['remove'] = remove


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    sp = subparser.add_subparsers(metavar='SUBCOMMAND', dest='subcommand')
    add_build_command(sp)
    add_remove_command(sp)


def cache(parser, args):
    _subcommands[args.subcommand](args)
