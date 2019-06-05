import os
import sys
import pymod.paths
from contrib.util.tty.pager import pager
from contrib.util.tty import redirect_stdout

try:
    import docutils
except ImportError:  # pragma: no cover
    docutils = None


description = "Display Modulecmd.py guides in the console"
section = "info"
level = "short"


available_guides = dict(
    [(os.path.splitext(f)[0], os.path.join(pymod.paths.docs_path, f))
     for f in os.listdir(pymod.paths.docs_path)])


def setup_parser(subparser):
    subparser.add_argument(
        'guide', choices=available_guides,
        help='Name of guide to display')


def guide(parser, args):
    if docutils is None:  # pragma: no cover
        raise ImportError('Guides require docutils module')
    import rst2ansi
    filename = available_guides[args.guide]
    with redirect_stdout():
        pager(rst2ansi.rst2ansi(open(filename, 'r').read()))
