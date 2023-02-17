import os
import sys
import argparse

import modulecmd.xio as xio
import modulecmd.modulepath as modulepath
import modulecmd.environ as environ
import modulecmd.config as config
from modulecmd.error import ModuleNotFoundError
from modulecmd._shell import modifies_shell_environment, set_shell


@modifies_shell_environment
def load(*args_in: str) -> None:
    ns = argparse.Namespace(name=args_in[0], args=[])
    groups = [ns]
    xio.trace(f"Loading the following modules: {', '.join(g.name for g in groups)}")
    for arg in args_in[1:]:
        if "=" in arg:
            ns.args.append(arg)
        else:
            ns = argparse.Namespace(name=arg, args=[])
            groups.append(ns)
    for group in groups:
        module = modulepath.find(group.name)
        if module is None:
            raise ModuleNotFoundError(group.name)
        module.load(group.args or None)


@modifies_shell_environment
def unload(*names: str) -> None:
    xio.trace(f"Unloading the following modules: {', '.join(names)}")
    for name in names:
        module = modulepath.find(name)
        if module is None:
            raise ModuleNotFoundError(name)
        elif module.loaded:
            module.unload()
        else:
            xio.warn(f"{module.fullname}: module is not loaded")


@modifies_shell_environment
def purge():
    xio.trace("Purging loaded modules")
    for module in reversed(environ.loaded()):
        if module.loaded:
            module.unload()


def show(*names: str) -> None:
    xio.trace(f"Showing sided effects of loading {', '.join(names)}")
    environ.set_mode("show")
    for name in names:
        module = modulepath.find(name)
        if module is None:
            raise ModuleNotFoundError(name)
        module.load()


def print_loaded() -> None:
    xio.trace("Listing loaded modules")
    loaded = environ.loaded_modules()
    if not loaded:
        xio.print("No loaded modules")
        return
    elements = []
    for (i, module) in enumerate(loaded):
        elements.append(f"{i+1}) {module['fullname']}")
    xio.print("Currently loaded modules")
    output = xio.colify(elements, indent=4)
    xio.print(output)


def avail(terse: bool = False) -> None:
    xio.trace("Showing available modules")
    for (path, modules) in modulepath.traverse():
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
                if module.is_default():
                    opts.append(xio.colorize("{bold}{red}D{endc}"))
                if module.loaded:
                    opts.append(xio.colorize("{bold}{green}L{endc}"))
                if opts:
                    name += f" ({','.join(opts)})"
                names.append(name)
            path = path.replace(os.path.expanduser("~"), "~")
            output = xio.colify(names)
            xio.cprint("{bold}{green}%s{endc}:" % path)
            if not output.split():
                width = xio.terminal_size().columns
                output = xio.colorize("{red}(None){endc}").center(width)
            xio.print(f"{output}\n")


def find(name: str) -> None:
    xio.trace(f"Finding {name!r}")
    module = modulepath.find_first(name)
    if module is None:
        xio.error(f"{name!r}: module not found")
    else:
        xio.print(module.file)


def cat(*names: str) -> None:
    xio.trace(f"Concatenating and printing {', '.join(names)}")
    for name in names:
        module = modulepath.find(name)
        if module is None:
            xio.error(f"{name}: module not found")
        else:
            xio.print(open(module.file).read())


def print_module_help(name: str) -> None:
    xio.trace(f"Printing help message for {name}")
    module = modulepath.find(name)
    if module is None:
        xio.error(f"{name}: module not found")
    else:
        module.print_help()


def print_module_short_description(name: str) -> None:
    xio.trace(f"Printing short description for {name}")
    module = modulepath.find(name)
    if module is None:
        xio.error(f"{name}: module not found")
    else:
        module.print_short_description()


def setup_parser(parser):
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

    p = parent.add_parser("avail", help="Print available modules")
    p.add_argument(
        "-t", "--terse", action="store_true", help="Print terse (single column) output"
    )

    p = parent.add_parser("find", help="Print the path module path")
    p.add_argument("name", help="Module name")

    p = parent.add_parser("load", help="Load the module[s]")
    p.add_argument("names", nargs="+", help="Module names")

    p = parent.add_parser("unload", help="Unload the module[s]")
    p.add_argument("names", nargs="+", help="Module names")

    p = parent.add_parser("cat", help="Concatenate and print module[s]")
    p.add_argument("names", nargs="+", help="Module names")

    p = parent.add_parser(
        "show", help="Show the commands that would be issued by module load"
    )
    p.add_argument("names", nargs="+", help="odule names")

    parent.add_parser("purge", help="Unload all loaded modules")
    parent.add_parser("list", aliases=["ls"], help="Unload all loaded modules")

    p = parent.add_parser("help", help="Print a module's help")
    p.add_argument("name", help="Module name")

    p = parent.add_parser("whatis", help="Print a module's short description")
    p.add_argument("name", help="Module name")


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
        find(args.name)
    elif args.subcommand == "avail":
        avail(terse=args.terse)
    elif args.subcommand == "cat":
        cat(*args.names)
    elif args.subcommand == "load":
        load(*args.names)
    elif args.subcommand == "unload":
        unload(*args.names)
    elif args.subcommand == "show":
        show(*args.names)
    elif args.subcommand == "purge":
        purge()
    elif args.subcommand in ("list", "ls"):
        print_loaded()
    elif args.subcommand == "help":
        print_module_help(args.name)
    elif args.subcommand == "whatis":
        print_module_short_description(args.name)
    else:
        parser.error("missing required subcommand")


if __name__ == "__main__":
    sys.exit(main())
