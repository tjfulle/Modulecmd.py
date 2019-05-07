import os

import pymod.mc
import pymod.names
import pymod.collection
from contrib.util import split

description = 'Initialize modules (should only be called by the startup script).'
level = 'long'
section = 'module'


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument(
        '-p', '--modulepath',
        default=os.getenv('MODULEPATH'),
        help='Initial MODULEPATH')


def init(parser, args):

    modulepath = split(args.modulepath, os.pathsep)
    for dirname in modulepath:
        pymod.mc.use(dirname, append=True)

    if pymod.collection.is_collection(pymod.names.default_user_collection):
        pymod.mc.restore(pymod.names.default_user_collection)

    pymod.mc.dump()
    return 0
