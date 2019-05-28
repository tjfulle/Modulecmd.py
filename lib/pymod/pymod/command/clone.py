import sys
import pymod.mc
import pymod.clone

description = 'Manipulate cloned environments'
level = 'short'
section = 'clones'


_subcommands = {}


def add_avail_command(parser):
    def avail(args):
        s = pymod.clone.avail(args.terse)
        sys.stderr.write(s)
    p = parser.add_parser('avail', help='List available (saved) clones')
    p.add_argument('-t', '--terse', action='store_true', help='Terse output')
    _subcommands['avail'] = avail


def add_save_command(parser):
    def save(args):
        return pymod.mc.clone.save(args.name)
    p = parser.add_parser('save', help='Save the current environment')
    p.add_argument('name', help='Name of clone')
    _subcommands['save'] = save


def add_remove_command(parser):
    def remove(args):
        return pymod.mc.clone.remove(args.name)
    p = parser.add_parser('remove', help='Remove clone')
    p.add_argument('name', help='Name of clone to remove')
    _subcommands['remove'] = remove


def add_restore_command(parser):
    def restore(args):
        pymod.mc.clone.restore(args.name)
        pymod.mc.dump()
    p = parser.add_parser('restore', help='Restore cloned environment')
    p.add_argument('name', help='Name of clone to restore')
    _subcommands['restore'] = restore


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    sp = subparser.add_subparsers(metavar='SUBCOMMAND', dest='subcommand')
    add_avail_command(sp)
    add_save_command(sp)
    add_remove_command(sp)
    add_restore_command(sp)


def clone(parser, args):
    _subcommands[args.subcommand](args)
