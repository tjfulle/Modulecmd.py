description = 'Displays available modules'
level = 'short'
section = 'module'


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
    print_available_modules(args.terse, args.regex, args.F)