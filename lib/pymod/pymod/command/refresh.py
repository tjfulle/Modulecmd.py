import pymod.mc


description = 'Remove and reload all loaded modules'
level = 'short'
section = 'module'


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    pass


def refresh(parser, args):
    pymod.mc.refresh()
    pymod.mc.dump()
