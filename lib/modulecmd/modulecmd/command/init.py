import os

import modulecmd.system
import modulecmd.names
import modulecmd.collection
from modulecmd.util.lang import split

description = "Initialize modules (should only be called by the startup script)."
level = "long"
section = "init"


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
    message with -h."""
    subparser.add_argument(
        "-p", "--modulepath", default=os.getenv("MODULEPATH"), help="Initial MODULEPATH"
    )


def init(parser, args):

    modulepath = split(args.modulepath, os.pathsep)
    modulecmd.system.init(modulepath)
    modulecmd.system.dump()
