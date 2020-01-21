import sys
import pymod.alias
import pymod.modulepath
from pymod.error import ModuleNotFoundError

description = "Create an alias to a module"
level = "short"
section = "basic"


_subcommands = {}


def add_avail_command(parser):
    def avail(args):
        s = pymod.alias.avail(terse=args.terse)
        sys.stderr.write(s)

    p = parser.add_parser("avail", help="List saved aliases")
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
        target = pymod.modulepath.get(args.target)
        if target is None:
            raise ModuleNotFoundError(args.target)
        pymod.alias.save(target, args.alias_name)

    p = parser.add_parser("save", help="Save the current environment")
    p.add_argument("target", help="Name of module to alias")
    p.add_argument("alias_name", help="Name of alias")
    _subcommands["save"] = save


def add_remove_command(parser):
    def remove(args):
        return pymod.alias.remove(args.name)

    p = parser.add_parser("remove", help="Remove alias")
    p.add_argument("name", help="Name of alias to remove")
    _subcommands["remove"] = remove


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    sp = subparser.add_subparsers(metavar="SUBCOMMAND", dest="subcommand")
    add_avail_command(sp)
    add_save_command(sp)
    add_remove_command(sp)


def alias(parser, args):
    _subcommands[args.subcommand](args)
