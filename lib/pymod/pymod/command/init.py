import os

import pymod.mc
import pymod.names
import pymod.collection
from contrib.util import split

description = "Initialize modules (should only be called by the startup script)."
level = "long"
section = "init"


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument(
        "-p", "--modulepath", default=os.getenv("MODULEPATH"), help="Initial MODULEPATH"
    )


def init(parser, args):

    modulepath = split(args.modulepath, os.pathsep)
    pymod.mc.init(modulepath)
    pymod.mc.dump()
