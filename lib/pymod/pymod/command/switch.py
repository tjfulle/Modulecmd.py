import os
import sys

import pymod.mc
import pymod.config
import pymod.environ
import llnl.util.tty as tty

description = "Switch from using Modulecmd.py to TCL module (or vice-versa)"
section = "developer"
level = "long"


def setup_parser(subparser):
    pass


def switch(parser, args):  # pragma: no cover
    s = pymod.shell.switch()
    if pymod.config.get('dryrun'):
        sys.stderr.write(s)
    else:
        pymod.mc.purge(load_after_purge=False)
        pymod.mc.dump()
        sys.stdout.write(s)
