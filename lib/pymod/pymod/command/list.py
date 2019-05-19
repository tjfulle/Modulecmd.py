import os
import sys
import pymod.mc
from contrib.util import split
from contrib.util.tty import grep_pat_in_string
from llnl.util.tty import terminal_size
from llnl.util.tty.colify import colified

description = 'Display loaded modules'
level = 'short'
section = 'info'


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


def list_loaded(args):
    lm_cellar = pymod.mc.get_cellar()
    if not lm_cellar:
        output = 'No loaded modules'

    else:
        loaded_modules = []
        for item in lm_cellar:
            fullname = item.fullname
            if item.opts:
                fullname += ' ' + ' '.join(item.opts)
            loaded_modules.append(fullname)

        if args.terse:
            output = '\n'.join(loaded_modules)
        elif args.show_command:
            output = ''
            for module in loaded_modules:
                output += 'module load {0}\n'.format(module)
        else:
            output = '\nCurrently loaded modules\n'
            loaded = ['{0}) {1}'.format(i+1, m) for i, m in enumerate(loaded_modules)]
            _, width = terminal_size()
            output += colified(loaded, indent=4, width=max(100, width))

        if args.regex:
            output = grep_pat_in_string(output, args.regex)

    sys.stderr.write(output)

def list(parser, args):
    list_loaded(args)
    return 0
