import modulecmd.system

description = "Unload and reload all loaded modules"
level = "short"
section = "basic"


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
    message with -h."""
    pass


def refresh(parser, args):
    modulecmd.system.refresh()
    modulecmd.system.dump()
