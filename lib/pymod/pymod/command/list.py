import os
import sys
import pymod.names
from contrib.util.misc import split
from contrib.util.logging.colify import colified

description = 'Display loaded modules'
level = 'short'
section = 'module'


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument(
        'regex', nargs='?',
        help='Regular expression to highlight in the output')
    subparser.add_argument(
        '-t', '--terse', default=False, action='store_true',
        help='Display output in terse format')
    subparser.add_argument(
        '-c', '--show-command', default=False, action='store_true',
        help='Display commands to load necessary to load the loaded modules')


def list(parser, args):
    loaded = split(os.getenv(pymod.names.loaded_modules), os.pathsep)
    if not loaded:
        output = 'No loaded modules'
    elif args.terse:
        output = '\n'.join(loaded)
    elif args.show_command:
        output = ''
        for module in loaded:
            output += 'module load {}\n'.format(module)
    else:
        output = '\nCurrently loaded modules\n'
        loaded = ['{}) {}'.format(i+1, m) for i, m in enumerate(loaded)]
        output += colified(loaded, indent=4)
    if args.regex:
        raise NotImplementedError('regex parsing not implmented')
    sys.stderr.write(output)
