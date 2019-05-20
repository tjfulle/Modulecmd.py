import pymod.mc

description = (
    "Display module whatis string.  The whatis string is a short informational\n"
    "message a module can provide.  If not defined by the module, a default is \n"
    "displayed.")
section = "info"
level = "short"


def setup_parser(subparser):
    subparser.add_argument(
        'modules', nargs='+',
        help='Display module whatis string')


def whatis(parser, args):
    for modulename in args.modules:
        pymod.mc.whatis(modulename)
        return 0
