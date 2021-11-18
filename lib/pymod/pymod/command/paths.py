import sys
import pymod.paths

description = "Show Modulecmd.py paths"
level = "short"
section = "developer"


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    pass


def add_path(a, name):
    path = getattr(pymod.paths, name)
    key = " ".join(name.split("_"))
    a.append((key, path))


def paths(parser, args):
    a = []
    add_path(a, "prefix")
    add_path(a, "user_config_path")
    n = max([len(x[0]) for x in a]) + 1
    for (name, path) in a:
        sys.stderr.write("{0:{1}s} {2}\n".format(name + ":", n, path))
