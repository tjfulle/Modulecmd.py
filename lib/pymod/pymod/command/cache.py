import pymod.modulepath

description = 'Cache modules on MODULEPATH'
level = 'short'
section = 'modulepath'


_subcommands = {}


def add_refresh_command(parser):
    def refresh(args):
        pymod.modulepath.refresh_cache()
    p = parser.add_parser('refresh', help='Refresh the MODULEPATH cache')
    _subcommands['refresh'] = refresh


def add_remove_command(parser):
    def remove(args):
        pymod.modulepath.remove_cache()
    p = parser.add_parser('remove', help='Remove the MODULEPATH cache')
    _subcommands['remove'] = remove


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    sp = subparser.add_subparsers(metavar='SUBCOMMAND', dest='subcommand')
    add_refresh_command(sp)
    add_remove_command(sp)


def cache(parser, args):
    _subcommands[args.subcommand](args)
