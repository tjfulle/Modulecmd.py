import os
import sys
import modulecmd.modulepath

description = "Show MODULEPATH"
level = "short"
section = "modulepath"


def setup_parser(subparser):
    pass


def path(parser, args):
    home = os.path.expanduser("~")
    paths = []
    for path in modulecmd.modulepath.path():
        paths.append(path.replace(home, "~"))
    s = "\n".join(
        "{0}) {1}".format(i, dirname) for i, dirname in enumerate(paths, start=1)
    )
    sys.stderr.write(s + "\n")
