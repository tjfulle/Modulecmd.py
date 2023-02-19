import os
import re
import sys
import argparse
from io import StringIO

import modulecmd.module
import modulecmd.tutorial
import modulecmd.xio as xio
import modulecmd.util as util
import modulecmd.config as config
import modulecmd.system as system
import modulecmd.modulepath as modulepath
import modulecmd._shell as shell
from modulecmd.error import ModuleNotFoundError


def find_modules(names):
    for name in names:
        s = None
        candidates = modulepath.candidates(name)
        if not candidates:
            raise ModuleNotFoundError(name)
        for module in candidates:
            s = "{bold}%s{endc}\n  {cyan}%s{endc}" % (module.fullname, module.file)
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
    file = StringIO()
    for (path, modules) in modulepath.items():
        if terse:
            names = [m.fullname for m in modules]
            file.write(f"{path}:\n")
            for name in names:
                file.write(name + "\n")
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
            xio.cprint("{bold}{green}%s{endc}:" % path, file=file)
            if not output.split():
                width = util.terminal_size().columns
                output = util.colorize("{red}(None){endc}").center(width)
            file.write(f"{output}\n")
    if showall:
        modulecmd.collection.format(terse=terse, regex=regex, file=file)
        modulecmd.clone.format_avail(file=file)


def print_module_contents(name, plain_pager=True):
    module = modulepath.get(name)
    text = open(module.file).read()
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
            s += "  {cyan}Filename:{endc}     %s\n" % module.file
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


def print_modulepath():
    home = os.path.expanduser("~")
    paths = []
    for path in modulepath.path():
        paths.append(path.replace(home, "~"))
    s = "\n".join(f"{i}) {dirname}" for i, dirname in enumerate(paths, start=1))
    xio.print(s)


def print_module_short_description(names):
    """Display 'whatis' message for the module given by `name`"""
    for name in names:
        module = modulepath.get(name)
        if module is None:
            raise ModuleNotFoundError(name, mp=modulepath)
        modulecmd.system.load_partial(module, mode=modulecmd.modes.whatis)
        s = module.format_whatis()
        xio.print(s)


def tutorial(action):
    if action == "basic":
        xio.info("Setting up Modulecmd.py's basic mock tutorial MODULEPATH")
        modulecmd.tutorial.basic_usage()
    elif action == "teardown":
        xio.info("Removing Modulecmd.py's mock tutorial MODULEPATH")
        modulecmd.tutorial.teardown()
    modulecmd.system.dump()


def print_guide(guide):
    import docutils
    from docutils import nodes, core  # noqa: F401
    import modulecmd.third_party.rst2ansi as rst2ansi

    filename = available_guides[guide]
    xio.pager(rst2ansi.rst2ansi(open(filename, "r").read()))


def print_module_help(name):
    """Display 'help' message for the module given by `modulename`"""
    module = modulepath.get(name)
    if module is None:
        raise ModuleNotFoundError(name, mp=modulepath)
    modulecmd.system.load_partial(module, mode=modulecmd.modes.help)
    s = module.format_help()
    xio.print(s)


@shell.modifies_shell_environment
def load_modules(*names, insert_at=None):
    groups = group_module_options(names)
    for (i, group) in enumerate(groups):
        insert_at = insert_at if i == 0 else None
        modulecmd.system.load(group.name, opts=group.args, insert_at=insert_at)


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

    p = parent.add_parser(
        "whatis",
        help="Display module whatis string.  The whatis string is a short informational\n"
        "message a module can provide.  If not defined by the module, a default is \n"
        "displayed.",
    )
    p.add_argument("names", nargs="+", help="Name of module")

    # ----

    p = parent.add_parser("find", help="Show path[s] to module[s]")
    p.add_argument("names", nargs="+", help="Name of module")

    # ----
    p = parent.add_parser(
        "cat", help="Print contents of a module or collection to the console output."
    )
    p.add_argument("name", help="Name of module, collection, or config file")

    # ---
    parent.add_parser("path", help="Show MODULEPATH")

    # ----
    p = parent.add_parser(
        "more",
        help="Print contents of a module or collection to the console output one\n"
        "page at a time.  Allows movement through files similar to shell's `less`\n"
        "program.",
    )
    p.add_argument("name", help="Name of module, collection, or config file")

    # ----
    p = parent.add_parser(
        "show", help="Show the commands that would be issued by module load"
    )
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
    p = parent.add_parser("load", help="Load modules into environment")
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
    p = parent.add_parser(
        "info", help="Provides information on a particular loaded module"
    )
    p.add_argument(
        "names", nargs="+", help="Name[s] of loaded modules to get information for"
    )

    # ----
    p = parent.add_parser(
        "tutorial", help="Setup or teardown Modulecmd.py's mock tutorial MODULEPATH"
    )
    p.add_argument(
        "action",
        choices=("basic", "teardown"),
        help="Setup or teardown Modulecmd.py's mock tutorial MODULEPATH",
    )

    # ----
    p = parent.add_parser("guide", help="Display Modulecmd.py guides in the console")
    p.add_argument("guide", choices=available_guides, help="Name of guide to display")

    p = parent.add_parser("help", help="Print module help pages")
    p.add_argument("name", help="Module to print help for")

    # -------------------------------------------------------------------------------- #
    # -------------------------------------------------------------------------------- #


available_guides = dict(
    [
        (os.path.splitext(f)[0], os.path.join(modulecmd.paths.docs_path, f))
        for f in os.listdir(modulecmd.paths.docs_path)
    ]
)


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
    elif args.subcommand == "path":
        print_modulepath()
    elif args.subcommand == "cat":
        print_module_contents(args.name, True)
    elif args.subcommand == "whatis":
        print_module_short_description(args.names)
    elif args.subcommand == "more":
        print_module_contents(args.name, False)
    elif args.subcommand == "load":
        load_modules(*args.args)
    elif args.subcommand == "unload":
        unload(*args.names)
    elif args.subcommand == "show":
        show_module_side_effects(*args.args)
    elif args.subcommand == "info":
        print_module_info(args.names)
    elif args.subcommand == "purge":
        purge()
    elif args.subcommand == "tutorial":
        tutorial(args.action)
    elif args.subcommand == "guide":
        print_guide(args.guide)
    elif args.subcommand in ("list", "ls"):
        print_loaded_modules(
            terse=args.terse, show_command=args.show_command, regex=args.regex
        )
    elif args.subcommand == "help":
        print_module_help(args.name)
    else:
        parser.error("missing required subcommand")


if __name__ == "__main__":
    sys.exit(main())
