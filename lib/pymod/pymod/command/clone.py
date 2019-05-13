import os
import sys
import pymod.mc

description = 'Clone current environment'
level = 'short'
section = 'collections'


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument(
        'name', help='Name to which current environment will be cloned')


def clone(parser, args):
    pymod.mc.clone(args.name)
