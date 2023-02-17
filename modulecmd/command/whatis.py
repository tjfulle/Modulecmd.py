import sys
import modulecmd.system

description = (
    "Display module whatis string.  The whatis string is a short informational\n"
    "message a module can provide.  If not defined by the module, a default is \n"
    "displayed."
)
section = "info"
level = "short"


def setup_parser(subparser):
    subparser.add_argument(
        "names", nargs="+", help="Module[s] to display whatis string"
    )


def whatis(parser, args):
    for name in args.names:
        s = modulecmd.system.whatis(name)
        sys.stderr.write(s + "\n")
