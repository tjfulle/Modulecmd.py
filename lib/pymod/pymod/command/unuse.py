import pymod.shell
import pymod.modulepath


description = 'Remove (unuse) directory[s] from MODULEPATH'
level = 'short'
section = 'module'


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument(
        'path', nargs='+',
        help='Path[s] to use.')


def unuse(parser, args):
    for path in args.path:
        pymod.modulepath.remove_path(path)
    pymod.shell.dump()
