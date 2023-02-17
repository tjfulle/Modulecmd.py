import modulecmd.xio as xio
import modulecmd.tutorial

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
        xio.info("Setting up Modulecmd.py's basic mock tutorial MODULEPATH")
        modulecmd.tutorial.basic_usage()
    elif args.action == "teardown":
        xio.info("Removing Modulecmd.py's mock tutorial MODULEPATH")
        modulecmd.tutorial.teardown()
    modulecmd.system.dump()
