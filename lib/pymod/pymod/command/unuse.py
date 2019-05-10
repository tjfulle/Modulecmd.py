import pymod.mc


description = 'Remove (unuse) directory[s] from MODULEPATH'
level = 'short'
section = 'module'


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument(
        'path', help='Path[s] to unuse.')


def unuse(parser, args):
    pymod.mc.unuse(args.path)
    pymod.mc.dump()
