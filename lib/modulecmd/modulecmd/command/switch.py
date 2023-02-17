import sys

import modulecmd.system
import modulecmd.config
import modulecmd.environ

description = "Switch from using Modulecmd.py to TCL module (or vice-versa)"
section = "developer"
level = "long"


def setup_parser(subparser):
    pass


def switch(parser, args):  # pragma: no cover
    s = modulecmd.shell.switch()
    if modulecmd.config.get("dryrun"):
        sys.stderr.write(s)
    else:
        modulecmd.system.purge(load_after_purge=False)
        modulecmd.system.dump()
        sys.stdout.write(s)
