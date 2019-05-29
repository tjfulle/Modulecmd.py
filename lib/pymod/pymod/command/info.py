import sys
import pymod.mc
from llnl.util.tty.color import colorize

description = 'Provides information on a particular loaded module'
level = 'short'
section = 'basic'


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument(
        'names', nargs='+',
        help='Name[s] of loaded modules to get information for')


def info(parser, args):
    loaded_modules = pymod.mc.get_loaded_modules()
    for name in args.names:
        for module in loaded_modules:
            if module.name == name or module.fullname == name:
                s = ('@B{Module:} @*{%s}\n'
                     '  @C{Name:}         %s\n'
                     '  @C{Version:}      %s\n'
                     '  @C{Modulepath:}   %s' % (
                         module.fullname, module.name, module.version,
                         module.modulepath)
                     )
                sys.stderr.write(colorize(s) + '\n')
                break
        else:
            raise ValueError('Module {0} is not loaded'.format(name))
