import pymod.tutorial
import llnl.util.tty as tty

description = "Setup or teardown Modulecmd.py's mock tutorial MODULEPATH"
section = "basic"
level = "short"


def setup_parser(subparser):
    subparser.add_argument(
        "action",
        choices=("basic", "teardown"),
        help="Setup or teardown Modulecmd.py's mock tutorial MODULEPATH",
    )


def tutorial(parser, args):
    if args.action == "basic":
        tty.info("Setting up Modulecmd.py's basic mock tutorial MODULEPATH")
        pymod.tutorial.basic_usage()
    elif args.action == "teardown":
        tty.info("Removing Modulecmd.py's mock tutorial MODULEPATH")
        pymod.tutorial.teardown()
    pymod.mc.dump()
