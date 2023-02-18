import os
import re
import sys
import argparse

import modulecmd.module
import modulecmd.xio as xio
import modulecmd.util as util
import modulecmd.config as config
import modulecmd.system as system
import modulecmd.modulepath as modulepath
from modulecmd._shell import set_shell
from modulecmd.error import ModuleNotFoundError


def find_modules(names):
    for name in names:
        s = None
        candidates = modulepath.candidates(name)
        if not candidates:
            raise ModuleNotFoundError(name)
        for module in candidates:
            s = "{bold}%s{endc}\n  {cyan}%s{endc}" % (module.fullname, module.filename)
            xio.print(util.colorize(s))


def print_loaded_modules(terse=False, show_command=False, regex=None) -> None:
    xio.trace("Listing loaded modules")
    Namespace = modulecmd.module.Namespace
    loaded = system.loaded_modules()
    if not loaded:
        xio.print("No loaded modules")
        return
    names = []
    for (i, module) in enumerate(loaded):
        name = module.fullname
        if module.opts:
            name += " " + Namespace(**(module.opts)).joined(" ")
        names.append(name)
    if terse:
        output = "\n".join(names)
    elif show_command:
        for name in names:
            xio.print(f"module load {name}")
    else:
        xio.print("Currently loaded modules")
        names = [f"{i + 1}) {m}" for (i, m) in enumerate(names)]
        output = util.colify(names, indent=4)
    if regex:
        output = util.grep_pat_in_string(output, regex, color="green")
    xio.print(output)


def print_available_modules(terse: bool = False, showall=False, regex=None) -> None:
    xio.trace("Showing avail,able modules")
    for (path, modules) in modulepath.items():
        if terse:
            names = [m.fullname for m in modules]
            xio.print(f"{path}:")
            for name in names:
                xio.print(name)
        else:
            names = []
            for module in modules:
                name = module.fullname
                opts = []
                if module.is_default:
                    opts.append(util.colorize("{bold}{red}D{endc}"))
                if module.is_loaded:
                    opts.append(util.colorize("{bold}{green}L{endc}"))
                if opts:
                    name += f" ({','.join(opts)})"
                names.append(name)
            path = path.replace(os.path.expanduser("~"), "~")
            output = util.colify(names)
            xio.cprint("{bold}{green}%s{endc}:" % path)
            if not output.split():
                width = util.terminal_size().columns
                output = util.colorize("{red}(None){endc}").center(width)
            xio.print(f"{output}\n")
    if showall:
        print_available_collections(terse=terse, regex=regex)
        avail += modulecmd.clone.avail(terse=terse)


def print_available_collections(terse=False, regex=None):
    skip = (modulecmd.names.default_user_collection,)
    names = sorted([_[0] for _ in modulecmd.collection.items() if _[0] not in skip])

    if regex:
        names = [c for c in names if re.search(regex, c)]

        if not names:  # pragma: no cover
            return

        if not terse:
            width = util.terminal_size().columns
            s = util.colify(names, width=width)
            # sio.write('{0}\n{1}\n'
            #          .format(' Saved collections '.center(width, '-'), s))
            xio.print(util.colorize("{green}Saved collections{endc}:\n%s" % (s)))
        else:
            xio.print("\n".join(c for c in names))


def print_clones(terse=False):
    names = sorted([x for x in modulecmd.clone.items()])
    if not names:  # pragma: no cover
        return
    if not terse:
        width = util.terminal_size().columns
        s = util.colify(names, width=width)
        xio.print("{0}\n{1}\n".format(" Saved clones ".center(width, "-"), s))
    else:
        xio.print("\n".join(c for c in names))
    return


def print_module_contents(name, plain_pager=True):
    module = modulepath.get(name)
    text = open(module.filename).read()
    xio.pager(text, plain=plain_pager)


def group_module_options(args):
    ns = argparse.Namespace(name=args[0], args=[])
    groups = [ns]
    xio.trace(f"Loading the following modules: {', '.join(g.name for g in groups)}")
    for arg in args[1:]:
        if "=" in arg:
            ns.args.append(arg)
        else:
            ns = argparse.Namespace(name=arg, args=[])
            groups.append(ns)
    return groups


def show_module_side_effects(*names, insert_at=None):
    groups = group_module_options(names)
    for (i, group) in enumerate(groups):
        insert_at = insert_at if i == 0 else None
        module = modulepath.get(group.name)
        if module is None:
            raise ModuleNotFoundError(group.name, mp=modulecmd.modulepath)
        if group.args:
            module.opts = group.args
        modulecmd.system.execmodule(module, modulecmd.modes.show)
        xio.print(modulecmd.system.state.cur_module_command_his.getvalue())


def print_module_info(names):
    for name in names:
        modules = modulepath.candidates(name)
        if not modules:
            raise ModuleNotFoundError(name)

        for module in modules:
            s = "{blue}Module:{endc} {bold}%s{endc}\n" % module.fullname
            s += "  {cyan}Name:{endc}         %s\n" % module.name

            if module.version:  # pragma: no cover
                s += "  {cyan}Version:{endc}      %s\n" % module.version

            if module.family:  # pragma: no cover
                s += "  {cyan}Family:{endc}      %s\n" % module.family

            s += "  {cyan}Loaded:{endc}       %s\n" % module.is_loaded
            s += "  {cyan}Filename:{endc}     %s\n" % module.filename
            s += "  {cyan}Modulepath:{endc}   %s" % module.modulepath

            unlocked_by = module.unlocked_by()
            if unlocked_by:  # pragma: no cover
                s += "  {cyan}Unlocked by:  %s\n"
                for m in unlocked_by:
                    s += "                    %s\n" % m.fullname

            unlocks = module.unlocks()
            if unlocks:  # pragma: no cover
                s += "  {cyan}Unlocks:{endc}      %s\n"
                for dirname in unlocks:
                    s += "                    %s\n" % dirname

            xio.print(util.colorize(s))


def setup_parser(parser):
    # -------------------------------------------------------------------------------- #
    # -------------------------------------------------------------------------------- #

    parser.add_argument(
        "-l",
        "--log-level",
        type=int,
        choices=(0, 1, 2, 3, 4),
        help="Log level.  0: error, 1: warn, 2: info, 3: debug, 4: trace [default: 2]",
    )
    parser.add_argument(
        "-d",
        "--dryrun",
        action="store_true",
        default=False,
        help="Print what would be executed by shell, but don't execute",
    )
    parser.add_argument(
        "-s",
        "--shell",
        choices=("sh", "bash", "csh", "tcsh"),
        help="Shell type.  By default the shell is determined from the environment",
    )
    parent = parser.add_subparsers(dest="subcommand", metavar="subcommand")

    # ---
    p = parent.add_parser("list", aliases=["ls"], help="Display loaded modules")

    # ---
    p = parent.add_parser("avail", help="Display available modules")
    p.add_argument(
        "-t",
        "--terse",
        default=False,
        action="store_true",
        help="Display output in terse format [default: %(default)s]",
    )
    p.add_argument(
        "-a",
        dest="showall",
        default=False,
        action="store_true",
        help="Include available clones and collections [default: %(default)s]",
    )
    p.add_argument(
        "regex",
        nargs="?",
        metavar="regex",
        help='Highlight available modules matching "regex"',
    )

    # ---

    p = parent.add_parser("list", aliases=["ls"], help="Display loaded modules")
    p.add_argument(
        "-t",
        "--terse",
        default=False,
        action="store_true",
        help="Display output in terse format",
    )
    p.add_argument(
        "-c",
        "--show-command",
        default=False,
        action="store_true",
        help="Display commands to load necessary to load the loaded modules",
    )
    p.add_argument(
        "regex", nargs="?", help="Regular expression to highlight in the output"
    )

    # ----

    p = parent.add_parser("find", help="Show path[s] to module[s]")
    p.add_argument("names", nargs="+", help="Name of module")

    # ----
    p = parent.add_parser("cat", help="Print contents of a module or collection to the console output.")
    p.add_argument("name", help="Name of module, collection, or config file")

    # ----
    p = parent.add_parser("more",
    help="Print contents of a module or collection to the console output one\n"
    "page at a time.  Allows movement through files similar to shell's `less`\n"
    "program.")
    p.add_argument("name", help="Name of module, collection, or config file")

    # ----
    p = parent.add_parser("show", help="Show the commands that would be issued by module load")
    p.add_argument(
        "-i",
        "--insert-at",
        type=int,
        default=None,
        help="Load the module as the `i`th module.",
    )
    p.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help=(
            "Modules and options to load. Additional options can be sent \n"
            "directly to the module using the syntax, `+option[=value]`. \n"
            "See the module options help for more details."
        ),
    )

    # ----
    p = parent.add_parser("info", help="Provides information on a particular loaded module")
    p.add_argument(
        "names", nargs="+", help="Name[s] of loaded modules to get information for"
    )

    # -------------------------------------------------------------------------------- #
    # -------------------------------------------------------------------------------- #



class argument_parser(argparse.ArgumentParser):
    def print_usage(self, file=None):
        super(argument_parser, self).print_usage(file=sys.stderr)

    def print_help(self, file=None):
        super(argument_parser, self).print_help(file=sys.stderr)

    def add_argument(self, *args, **kwargs):
        default = kwargs.get("default")
        help_message = kwargs.get("help")
        if default not in (None, argparse.SUPPRESS) and help_message is not None:
            kwargs["help"] = f"{help_message} [default: {default}]"
        super(argument_parser, self).add_argument(*args, **kwargs)


def main(argv=None):
    argv = argv or sys.argv[1:]
    parser = argument_parser(prog="module")
    setup_parser(parser)
    args = parser.parse_args()

    if args.log_level is not None:
        map: dict[int, int] = {
            0: xio.ERROR,
            1: xio.WARN,
            2: xio.INFO,
            3: xio.DEBUG,
            4: xio.TRACE,
        }
        level: int = map[args.log_level]
        xio.set_log_level(level)

    if args.shell is not None:
        set_shell(args.shell)

    if args.dryrun:
        config.set("dryrun", True)

    if args.subcommand == "find":
        find_modules(args.names)
    elif args.subcommand == "avail":
        print_available_modules(
            terse=args.terse, showall=args.showall, regex=args.regex
        )
    elif args.subcommand == "cat":
        print_module_contents(args.name, True)
    elif args.subcommand == "more":
        print_module_contents(args.name, False)
    elif args.subcommand == "load":
        load(*args.names)
    elif args.subcommand == "unload":
        unload(*args.names)
    elif args.subcommand == "show":
        show_module_side_effects(*args.args)
    elif args.subcommand == "info":
        print_module_info(args.names)
    elif args.subcommand == "purge":
        purge()
    elif args.subcommand in ("list", "ls"):
        print_loaded_modules(
            terse=args.terse, show_command=args.show_command, regex=args.regex
        )
    elif args.subcommand == "help":
        print_module_help(args.name)
    elif args.subcommand == "whatis":
        print_module_short_description(args.name)
    else:
        parser.error("missing required subcommand")


if __name__ == "__main__":
    sys.exit(main())
