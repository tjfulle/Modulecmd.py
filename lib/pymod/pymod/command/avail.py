import sys

import pymod.modulepath
import pymod.collection


description = 'Displays available modules'
level = 'short'
section = 'basic'


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument(
        'regex', nargs='?', metavar='regex',
        help='Highlight available modules matching "regex"')
    subparser.add_argument(
        '-t', '--terse', default=False, action='store_true',
        help='Display output in terse format [default: %(default)s]')
    subparser.add_argument(
        '-F', default=False, action='store_true',
        help='Display full output [default: %(default)s]')


def avail(parser, args):
    avail = pymod.modulepath.format_available(
        terse=args.terse, regex=args.regex, fulloutput=args.F)
    avail += pymod.collection.format_available(
        terse=args.terse, regex=args.regex)
    sys.stderr.write(avail)
