import sys
import pymod.alias
import pymod.modulepath
from pymod.error import ModuleNotFoundError

description = 'Create an alias to a module'
level = 'short'
section = 'basic'


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument('target', help='Name of module to alias')
    subparser.add_argument('alias_name', help='Name of alias')


def alias(parser, args):
    target = pymod.modulepath.get(args.target)
    if target is None:
        raise ModuleNotFoundError(args.target)
    pymod.alias.save(target, args.alias_name)
