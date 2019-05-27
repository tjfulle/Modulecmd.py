import sys
import pymod.mc

description = 'Clone current environment'
level = 'short'
section = 'clones'


_subcommands = {}


def add_save_command(parser):
    p = parser.add_parser('save', help='Save the current environment')
    p.add_argument('name', help='Name of clone')
    _subcommands['save'] = lambda args: pymod.mc.clone(args.name)


def add_list_command(parser):
    p = parser.add_parser('list', help='List clones')
    _subcommands['list'] = lambda _: sys.stderr.write(pymod.mc.list_clones()+'\n')


def add_remove_command(parser):
    p = parser.add_parser('remove', help='Remove clone')
    p.add_argument('name', help='Name of clone to remove')
    _subcommands['remove'] = lambda args: pymod.mc.remove_clone(args.name)


def add_restore_command(parser):
    p = parser.add_parser('restore', help='Restore cloned environment')
    p.add_argument('name', help='Name of clone to restore')
    _subcommands['restore'] = lambda args: pymod.mc.restore_clone(args.name)


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    sp = subparser.add_subparsers(metavar='SUBCOMMAND', dest='subcommand')
    add_save_command(sp)
    add_remove_command(sp)
    add_restore_command(sp)
    add_list_command(sp)


def clone(parser, args):
    _subcommands[args.subcommand](args)