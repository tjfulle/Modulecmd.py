import os
import argparse

import pymod.mc
from pymod.command.common import parse_module_options

description = "Show the commands that would be issued by module load"
level = "short"
section = "info"


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument(
        "-i",
        "--insert-at",
        type=int,
        default=None,
        help="Load the module as the `i`th module.",
    )
    subparser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help=(
            "Modules and options to load. Additional options can be sent \n"
            "directly to the module using the syntax, `+option[=value]`. \n"
            "See the module options help for more details."
        ),
    )


def show(parser, args):
    argv = parse_module_options(args.args)
    for (i, spec) in enumerate(argv):
        insert_at = args.insert_at if i == 0 else None
        name = (
            spec["name"]
            if spec["version"] is None
            else os.path.sep.join([spec["name"], spec["version"]])
        )
        pymod.mc.show(name, opts=spec["options"], insert_at=insert_at)
