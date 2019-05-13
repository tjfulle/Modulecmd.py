import os
import sys
import pymod.names
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
    loaded_modules = pymod.environ.get_path(pymod.names.loaded_modules)
    if not loaded_modules:
        output = 'No loaded modules'

    else:
        loaded_module_opts = pymod.environ.get_dict(pymod.names.loaded_module_opts)
        for (i, module) in enumerate(loaded_modules):
            opts = loaded_module_opts.get(module)
            if opts is not None:
                loaded_modules[i] = module + ' ' + ' '.join(opts)

        if args.terse:
            output = '\n'.join(loaded_modules)
        elif args.show_command:
            output = ''
            for module in loaded_modules:
                output += 'module load {}\n'.format(module)
        else:
            output = '\nCurrently loaded modules\n'
            loaded = ['{}) {}'.format(i+1, m) for i, m in enumerate(loaded_modules)]
            _, width = terminal_size()
            output += colified(loaded, indent=4, width=max(100, width))

        if args.regex:
            output = grep_pat_in_string(output, args.regex)

    sys.stderr.write(output)

def list(parser, args):
    list_loaded(args)
    return 0
