import argparse
import modulecmd.system

description = "Unload modules from environment"
level = "short"
section = "basic"


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
    message with -h."""
    subparser.add_argument("names", nargs=argparse.REMAINDER, help="Modules to unload")


def unload(parser, args):
    for name in args.names:
        modulecmd.system.unload(name)
    modulecmd.system.dump()
