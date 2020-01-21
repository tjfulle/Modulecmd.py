import pymod.mc

description = "Reset environment to initial state"
level = "short"
section = "basic"


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """


def reset(parser, args):
    pymod.mc.reset()
    pymod.mc.dump()
