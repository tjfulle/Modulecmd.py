import pymod.discover
import pymod.modulepath

description = 'Cache modules on MODULEPATH'
level = 'short'
section = 'modulepath'


_subcommands = {}


def add_create_command(parser):
    def create(args):
        pymod.discover.remove_cache()
        # calling any modulepath function will cause the cache to be created.
        # There isn't a create_create() method since it would depend on
        # pymod.modulepath, creating a circular dependency
        pymod.modulepath.size()
    p = parser.add_parser('create', help='Create the MODULEPATH cache')
    _subcommands['create'] = create

def add_refresh_command(parser):
    def refresh(args):
        pymod.discover.refresh_cache()
    p = parser.add_parser('refresh', help='Refresh the MODULEPATH cache')
    _subcommands['refresh'] = refresh


def add_remove_command(parser):
    def remove(args):
        pymod.discover.remove_cache()
    p = parser.add_parser('remove', help='Remove the MODULEPATH cache')
    _subcommands['remove'] = remove


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    sp = subparser.add_subparsers(metavar='SUBCOMMAND', dest='subcommand')
    add_create_command(sp)
    add_refresh_command(sp)
    add_remove_command(sp)


def cache(parser, args):
    _subcommands[args.subcommand](args)
