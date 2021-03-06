import pymod.mc
import pymod.shell
import pymod.modulepath


description = "Add (use) directory[s] to MODULEPATH"
level = "short"
section = "modulepath"


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument("path", help="Path[s] to use.")
    subparser.add_argument(
        "-a",
        "--append",
        default=False,
        action="store_true",
        help="Append path[s] to MODULEPATH, otherwise prepend",
    )
    subparser.add_argument(
        "-D",
        "--delete",
        default=False,
        action="store_true",
        help=(
            "Remove path[s] from MODULEPATH instead of adding. "
            "Behaves identically to `unuse`"
        ),
    )


def use(parser, args):
    pymod.mc.use(args.path, delete=args.delete, append=args.append)
    pymod.mc.dump()
