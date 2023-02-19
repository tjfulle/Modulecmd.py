import os
import re
import sys
import argparse
from io import StringIO

import modulecmd.paths
import modulecmd.module
import modulecmd.tutorial
import modulecmd.xio as xio
import modulecmd.util as util
import modulecmd.config as config
import modulecmd.system as system
import modulecmd.modulepath as modulepath
import modulecmd._shell as shell
from modulecmd.error import ModuleNotFoundError
from modulecmd._util.tty import redirect_stdout2 as redirect_stdout


# --- ALIAS -------------------------------------------------------------------------- #
def setup_alias_parser(parser):
    sp = parser.add_subparsers(metavar="alias subcommand", dest="alias_command")
    p = sp.add_parser("avail", help="List saved aliases")
    p.add_argument(
        "-t",
        "--terse",
        action="store_true",
        default=False,
        help="Display output in terse format [default: %(default)s]",
    )
    p = sp.add_parser("save", help="Save the current environment")
    p.add_argument("source", help="Name of module to alias")
    p.add_argument("alias_name", help="Name of alias")
    p = sp.add_parser("remove", help="Remove alias")
    p.add_argument("name", help="Name of alias to remove")


def alias(subcommand, args):
    if subcommand == "save":
        save_alias(args.source, args.aliase_name)
    elif subcommand == "avail":
        available_aliases(terse=args.terse)
    elif subcommand == "remove":
        remove_alias(args.name)


def available_aliases(terse=False):
    s = modulecmd.alias.avail(terse=terse)
    xio.print(s)


def save_alias(source, alias_name):
    module = modulepath.get(source)
    if source is None:
        raise ModuleNotFoundError(source)
    modulecmd.alias.save(module, alias_name)


def remove_alias(name):
    modulecmd.alias.remove(name)


# --- COLLECTION --------------------------------------------------------------------- #
def setup_collection_parser(parser):
    sp = parser.add_subparsers(metavar="collection subcommand", dest="c_command")
    p = sp.add_parser("avail", help="List available (saved) collections")
    p.add_argument(
        "regex",
        nargs="?",
        metavar="regex",
        help='Highlight available modules matching "regex"',
    )
    p.add_argument(
        "-t",
        "--terse",
        action="store_true",
        default=False,
        help="Display output in terse format [default: %(default)s]",
    )
    p = sp.add_parser("save", help="Save the current environment")
    p.add_argument(
        "name",
        nargs="?",
        default=modulecmd.names.default_user_collection,
        help="Name of collection to save",
    )
    p = sp.add_parser("add", help="Add module to currently loaded collection")
    p.add_argument(
        "name",
        default=modulecmd.names.default_user_collection,
        help="Name of module to add to currently loaded collection",
    )
    p = sp.add_parser("pop", help="Pop module from currently loaded collection")
    p.add_argument(
        "name",
        default=modulecmd.names.default_user_collection,
        help="Name of module to pop from currently loaded collection",
    )
    p = sp.add_parser(
        "show", help="Show actions that would be taken by restoring the collection"
    )
    p.add_argument(
        "name",
        nargs="?",
        default=modulecmd.names.default_user_collection,
        help="Name of collection to show",
    )
    p = sp.add_parser("remove", help="Remove collection")
    p.add_argument("name", help="Name of collection to remove")
    p = sp.add_parser("restore", help="Restore collection")
    p.add_argument(
        "name",
        nargs="?",
        default=modulecmd.names.default_user_collection,
        help="Name of collection to restore",
    )


def collection(subcommand, args):
    if subcommand == "avail":
        return avail_collections(terse=args.terse, regex=args.regex)
    elif subcommand == "save":
        return save_collection(args.name)
    elif subcommand == "add":
        return add_to_collection(args.name)
    elif subcommand == "pop":
        return pop_from_collection(args.name)
    elif subcommand == "show":
        return show_collection(args.name)
    elif subcommand == "remove":
        return remove_collection(args.name)
    elif subcommand == "restore":
        return restore_collection(args.name)


def avail_collections(terse=False, regex=None):
    s = modulecmd.collection.format_avail(terse=terse, regex=regex)
    xio.print(s)


def save_collection(name):
    return modulecmd.system.save_collection(name)


def add_to_collection(name):
    return modulecmd.system.add_to_loaded_collection(name)


def pop_from_collection(name):
    return modulecmd.system.pop_from_loaded_collection(name)


def show_collection(name):
    return modulecmd.system.show_collection(name)


def remove_collection(name):
    return modulecmd.system.remove_collection(name)


@shell.modifies_shell_environment
def restore_collection(name):
    modulecmd.system.restore_collectionstore(name)


# --- FIND --------------------------------------------------------------------------- #
def setup_find_parser(parser):
    parser.add_argument("names", nargs="+", help="Name of module")


def find_modules(names):
    for name in names:
        s = None
        candidates = modulepath.candidates(name)
        if not candidates:
            raise ModuleNotFoundError(name)
        for module in candidates:
            s = "{bold}%s{endc}\n  {cyan}%s{endc}" % (module.fullname, module.file)
            xio.print(util.colorize(s))


# --- LIST --------------------------------------------------------------------------- #
def setup_list_parser(parser):
    parser.add_argument(
        "-t",
        "--terse",
        default=False,
        action="store_true",
        help="Display output in terse format",
    )
    parser.add_argument(
        "-c",
        "--show-command",
        default=False,
        action="store_true",
        help="Display commands to load necessary to load the loaded modules",
    )
    parser.add_argument(
        "regex", nargs="?", help="Regular expression to highlight in the output"
    )


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


# --- AVAIL -------------------------------------------------------------------------- #
def setup_avail_parser(parser):
    parser.add_argument(
        "-t",
        "--terse",
        default=False,
        action="store_true",
        help="Display output in terse format [default: %(default)s]",
    )
    parser.add_argument(
        "-a",
        dest="showall",
        default=False,
        action="store_true",
        help="Include available clones and collections [default: %(default)s]",
    )
    parser.add_argument(
        "regex",
        nargs="?",
        metavar="regex",
        help='Highlight available modules matching "regex"',
    )


def print_available_modules(terse: bool = False, showall=False, regex=None) -> None:
    xio.trace("Showing avail,able modules")
    file = StringIO()
    modulepath.format_avail(terse=terse, regex=regex, file=file)
    if showall:
        modulecmd.collection.format_avail(terse=terse, regex=regex, file=file)
        modulecmd.clone.format_avail(file=file)
    xio.print(file.getvalue().rstrip())


# --- CAT/MORE ----------------------------------------------------------------------- #
def setup_cat_parser(parser):
    parser.add_argument("name", help="Name of module, collection, or config file")


def cat_module(name, plain_pager=True):
    module = modulepath.get(name)
    text = open(module.file).read()
    xio.pager(text, plain=plain_pager)


# --- LOAD --------------------------------------------------------------------------- #
def setup_load_parser(parser):
    parser.add_argument(
        "-i",
        "--insert-at",
        type=int,
        default=None,
        help="Load the module as the `i`th module.",
    )
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help=(
            "Modules and options to load. Additional options can be sent \n"
            "directly to the module using the syntax, `+option[=value]`. \n"
            "See the module options help for more details."
        ),
    )


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


@shell.modifies_shell_environment
def load_modules(*names, insert_at=None):
    groups = group_module_options(names)
    for (i, group) in enumerate(groups):
        insert_at = insert_at if i == 0 else None
        modulecmd.system.load(group.name, opts=group.args, insert_at=insert_at)


# --- SHOW --------------------------------------------------------------------------- #
def setup_show_parser(parser):
    parser.add_argument(
        "-i",
        "--insert-at",
        type=int,
        default=None,
        help="Load the module as the `i`th module.",
    )
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help=(
            "Modules and options to load. Additional options can be sent \n"
            "directly to the module using the syntax, `+option[=value]`. \n"
            "See the module options help for more details."
        ),
    )


def show_modules(*names, insert_at=None):
    groups = group_module_options(names)
    for (i, group) in enumerate(groups):
        insert_at = insert_at if i == 0 else None
        module = modulepath.get(group.name)
        if module is None:
            raise ModuleNotFoundError(group.name, mp=modulepath)
        if group.args:
            module.opts = group.args
        modulecmd.system.execmodule(module, modulecmd.modes.show)
        xio.print(modulecmd.system.state.cur_module_command_his.getvalue())


# --- INFO --------------------------------------------------------------------------- #
def setup_info_parser(parser):
    parser.add_argument(
        "names", nargs="+", help="Name[s] of loaded modules to get information for"
    )


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


# --- PATH --------------------------------------------------------------------------- #
def setup_path_parser(parser):
    pass


def print_modulepath():
    home = os.path.expanduser("~")
    paths = []
    for path in modulepath.path():
        paths.append(path.replace(home, "~"))
    s = "\n".join(f"{i}) {dirname}" for i, dirname in enumerate(paths, start=1))
    xio.print(s)


# --- WHATIS ------------------------------------------------------------------------- #
def setup_whatis_parser(parser):
    parser.add_argument("names", nargs="+", help="Name of module")


def print_whatis(names):
    """Display 'whatis' message for the module given by `name`"""
    for name in names:
        module = modulepath.get(name)
        if module is None:
            raise ModuleNotFoundError(name, mp=modulepath)
        modulecmd.system.load_partial(module, mode=modulecmd.modes.whatis)
        s = module.format_whatis()
        xio.print(s)


# --- TUTORIAL ----------------------------------------------------------------------- #
def setup_tutorial_parser(parser):
    parser.add_argument(
        "action",
        choices=("basic", "teardown"),
        help="Setup or teardown Modulecmd.py's mock tutorial MODULEPATH",
    )


def tutorial(action):
    if action == "basic":
        xio.info("Setting up Modulecmd.py's basic mock tutorial MODULEPATH")
        modulecmd.tutorial.basic_usage()
    elif action == "teardown":
        xio.info("Removing Modulecmd.py's mock tutorial MODULEPATH")
        modulecmd.tutorial.teardown()
    modulecmd.system.dump()


# --- GUIDE -------------------------------------------------------------------------- #
def setup_guide_parser(parser):
    parser.add_argument(
        "guide", choices=available_guides, help="Name of guide to display"
    )


def print_guide(guide):
    import docutils  # noqa: F401
    from docutils import nodes, core  # noqa: F401
    import modulecmd.third_party.rst2ansi as rst2ansi

    filename = available_guides[guide]
    xio.pager(rst2ansi.rst2ansi(open(filename, "r").read()))


# --- HELP --------------------------------------------------------------------------- #
def setup_help_parser(parser):
    parser.add_argument("name", help="Module to print help for")


def print_module_help(name):
    """Display 'help' message for the module given by `modulename`"""
    module = modulepath.get(name)
    if module is None:
        raise ModuleNotFoundError(name, mp=modulepath)
    modulecmd.system.load_partial(module, mode=modulecmd.modes.help)
    s = module.format_help()
    xio.print(s)


# --- UNLOAD ------------------------------------------------------------------------- #
def setup_unload_parser(parser):
    parser.add_argument("names", nargs=argparse.REMAINDER, help="Modules to unload")


@shell.modifies_shell_environment
def unload_modules(*names):
    for name in names:
        modulecmd.system.unload(name)


# --- PURGE -------------------------------------------------------------------------- #
def setup_purge_parser(parser):
    parser.add_argument(
        "-F",
        default=None,
        action="store_true",
        help="Do not load modules in `load_after_purge` configuration",
    )


@shell.modifies_shell_environment
def purge_loaded(load_after_purge=True):
    modulecmd.system.purge(load_after_purge=load_after_purge)


# --- RELOAD ------------------------------------------------------------------------- #
def setup_reload_parser(parser):
    parser.add_argument("name", help="Module to reload")


@shell.modifies_shell_environment
def reload_module(name):
    modulecmd.system.reload(name)


# --- USE ---------------------------------------------------------------------------- #
def setup_use_parser(parser):
    parser.add_argument("path", help="Path to use.")
    parser.add_argument(
        "-a",
        "--append",
        default=False,
        action="store_true",
        help="Append path to MODULEPATH, otherwise prepend",
    )
    parser.add_argument(
        "-D",
        "--delete",
        default=False,
        action="store_true",
        help=(
            "Remove path from MODULEPATH instead of adding. "
            "Behaves identically to `unuse`"
        ),
    )


@shell.modifies_shell_environment
def use_path(path, delete=False, append=False):
    modulecmd.system.use(path, delete=delete, append=append)


# --- UNUSE -------------------------------------------------------------------------- #
def setup_unuse_parser(parser):
    parser.add_argument("path", help="Path to unuse.")


@shell.modifies_shell_environment
def unuse_path(path):
    modulecmd.system.unuse(path)


# --- REFRESH ------------------------------------------------------------------------ #
def setup_refresh_parser(parser):
    pass


@shell.modifies_shell_environment
def refresh_modules():
    modulecmd.system.refresh()


# --- SWAP --------------------------------------------------------------------------- #
def setup_swap_parser(parser):
    parser.add_argument("first", help="Module to unload")
    parser.add_argument("second", help="Module to load")


@shell.modifies_shell_environment
def swap_modules(first, second):
    modulecmd.system.swap(first, second)


# --- CLONE -------------------------------------------------------------------------- #
def setup_clone_parser(parser):
    sp = parser.add_subparsers(metavar="clone subcommand", dest="c_command")
    p = sp.add_parser("avail", help="List available (saved) clones")
    p.add_argument("-t", "--terse", action="store_true", help="Terse output")
    p = sp.add_parser("save", help="Save the current environment")
    p.add_argument("name", help="Name of clone")
    p = sp.add_parser("remove", help="Remove clone")
    p.add_argument("name", help="Name of clone to remove")
    p = sp.add_parser("restore", help="Restore cloned environment")
    p.add_argument("name", help="Name of clone to restore")


def clone(subcommand, args):
    if subcommand == "avail":
        return available_clones(terse=args.terse)
    elif subcommand == "save":
        return save_clone(args.name)
    elif subcommand == "remove":
        return remove_clone(args.name)
    elif subcommand == "restore":
        return restore_clone(args.name)


def available_clones(terse=False):
    s = modulecmd.clone.avail(terse=terse)
    sys.stderr.write(s)


def save_clone(name):
    return modulecmd.system.save_clone(name)


def remove_clone(name):
    return modulecmd.system.remove_clone(name)


@shell.modifies_shell_environment
def restore_clone(name):
    modulecmd.system.restore_clone(name)


# --- RESET -------------------------------------------------------------------------- #
def setup_reset_parser(parser):
    pass


@shell.modifies_shell_environment
def reset():
    modulecmd.system.reset()


# ---- INIT -------------------------------------------------------------------------- #
def setup_init_parser(parser):
    parser.add_argument(
        "-p", "--modulepath", default=os.getenv("MODULEPATH"), help="Initial MODULEPATH"
    )


@shell.modifies_shell_environment
def init(path):
    path = util.split(path, os.pathsep)
    modulecmd.system.init(path)


# ---- CACHE ------------------------------------------------------------------------- #
def setup_cache_parser(parser):
    sp = parser.add_subparsers(metavar="cache subcommands", dest="c_command")
    sp.add_parser("build", help="Build the module cache")
    sp.add_parser("rebuild", help="Rebuild the module cache")
    sp.add_parser("remove", help="Remove the module cache")


def cache(command):
    if command == "build":
        modulecmd.cache.build()
    elif command == "rebuild":
        modulecmd.cache.remove()
        modulecmd.cache.build()
    elif command == "remove":
        modulecmd.cache.remove()


# ---- TEST -------------------------------------------------------------------------- #
def setup_test_parser(parser):
    parser.add_argument(
        "-H",
        "--pytest-help",
        action="store_true",
        default=False,
        help="print full pytest help message, showing advanced options",
    )

    list_group = parser.add_mutually_exclusive_group()
    list_group.add_argument(
        "-l", "--list", action="store_true", default=False, help="list basic test names"
    )
    list_group.add_argument(
        "-L",
        "--long-list",
        action="store_true",
        default=False,
        help="list the entire hierarchy of tests",
    )
    parser.add_argument(
        "tests",
        nargs=argparse.REMAINDER,
        help="list of tests to run (will be passed to pytest -k)",
    )


def do_list(args):
    """Print a lists of tests than what pytest offers."""
    # Run test collection and get the tree out.
    import pytest

    old_output = sys.stderr
    try:
        sys.stderr = output = StringIO()
        pytest.main(["--collect-only"])
    finally:
        sys.stderr = old_output

    # put the output in a more readable tree format.
    lines = output.getvalue().split("\n")
    output_lines = []
    for line in lines:
        match = re.match(r"(\s*)<([^ ]*) '([^']*)'", line)
        if not match:
            continue
        indent, nodetype, name = match.groups()

        # only print top-level for short list
        if args.list:
            if not indent:
                output_lines.append(os.path.basename(name).replace(".py", ""))
        else:
            sys.stderr.write(indent + name)

    if args.list:
        util.colify(output_lines) + "\n"


def test(args, unknown_args):
    import pytest

    if args.pytest_help:
        # make the pytest.main help output more accurate
        with redirect_stdout():
            sys.argv[0] = "modulecmd test"
            pytest.main(["-h"])
        return

    pytest_root = modulecmd.paths.test_path

    # pytest.ini lives in the root of the modulecmd repository.
    with redirect_stdout():
        with util.working_dir(pytest_root):
            # --list and --long-list print the test output better.
            if args.list or args.long_list:
                do_list(args, unknown_args)
                return

            # Allow keyword search without -k if no options are specified
            if (
                args.tests
                and not unknown_args
                and not any(arg.startswith("-") for arg in args.tests)
            ):
                return pytest.main(["-k"] + args.tests)

            # Just run the pytest command
            return pytest.main(unknown_args + args.tests)


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
        "--dryrun",
        action="store_true",
        default=False,
        help="Print what would be executed by shell, but don't execute",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        default=False,
        help="Debug modde",
    )
    parser.add_argument(
        "-s",
        "--shell",
        choices=("sh", "bash", "csh", "tcsh"),
        help="Shell type.  By default the shell is determined from the environment",
    )
    parent = parser.add_subparsers(dest="subcommand", metavar="subcommand")

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser("alias", help="Create aliases to modules")
    setup_alias_parser(p)

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser("avail", help="Display available modules")
    setup_avail_parser(p)

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser("list", aliases=["ls"], help="Display loaded modules")
    setup_list_parser(p)

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser(
        "whatis",
        help="Display module whatis string.  The whatis string is a short informational\n"
        "message a module can provide.  If not defined by the module, a default is \n"
        "displayed.",
    )
    setup_whatis_parser(p)

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser("find", help="Show path[s] to module[s]")
    setup_find_parser(p)

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser("path", help="Show MODULEPATH")
    setup_path_parser(p)

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser(
        "cat", help="Print contents of a module or collection to the console output."
    )
    setup_cat_parser(p)

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser(
        "more",
        help="Print contents of a module or collection to the console output one\n"
        "page at a time.  Allows movement through files similar to shell's `less`\n"
        "program.",
    )
    setup_cat_parser(p)

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser(
        "show", help="Show the commands that would be issued by module load"
    )
    setup_show_parser(p)

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser("load", help="Load modules into environment")
    setup_load_parser(p)

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser("unload", help="Unload modules")
    setup_unload_parser(p)

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser(
        "info", help="Provides information on a particular loaded module"
    )
    setup_info_parser(p)

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser(
        "tutorial", help="Setup or teardown Modulecmd.py's mock tutorial MODULEPATH"
    )
    setup_tutorial_parser(p)

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser("guide", help="Display Modulecmd.py guides in the console")
    setup_guide_parser(p)

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser("help", help="Print module help pages")
    setup_help_parser(p)

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser("purge", help="Purge (unload) all loaded modules")
    setup_purge_parser(p)

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser("reload", help="Reload loaded module")

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser("use", help="Add (use) directory to MODULEPATH")
    setup_use_parser(p)

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser("unuse", help="Remove from MODULEPATH")
    setup_unuse_parser(p)

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser(
        "swap",
        help="Swap two modules, effectively unloading the first then loading the second",
    )
    setup_swap_parser(p)

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser("refresh", help="Unload and reload all loaded modules")
    setup_refresh_parser(p)

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser("collection", help="Manage module collections")
    setup_collection_parser(p)

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser("clone", help="Manage cloned environments")
    setup_clone_parser(p)

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser("reset", help="Reset environment to initial state")
    setup_reset_parser(p)

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser(
        "init", help="Initialize modules (should only be called by the startup script)."
    )
    setup_init_parser(p)

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser("cache", help="Manage module cache")
    setup_cache_parser(p)

    # --------------------------------------------------------------------------------- #
    p = parent.add_parser("test", help="Run unit tests")
    setup_test_parser(p)

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


def main2(parser, args, unknown_args):
    if args.subcommand == "alias":
        return alias(args.alias_subcommand, args)
    elif args.subcommand == "find":
        find_modules(args.names)
    elif args.subcommand == "avail":
        print_available_modules(
            terse=args.terse, showall=args.showall, regex=args.regex
        )
    elif args.subcommand == "path":
        print_modulepath()
    elif args.subcommand == "cat":
        cat_module(args.name, True)
    elif args.subcommand == "whatis":
        print_whatis(args.names)
    elif args.subcommand == "more":
        cat_module(args.name, False)
    elif args.subcommand == "load":
        load_modules(*args.args)
    elif args.subcommand == "unload":
        unload_modules(*args.names)
    elif args.subcommand == "show":
        show_modules(*args.args)
    elif args.subcommand == "info":
        print_module_info(args.names)
    elif args.subcommand == "purge":
        purge_loaded(load_after_purge=not args.F)
    elif args.subcommand == "reload":
        reload_module(args.name)
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
    elif args.subcommand == "use":
        use_path(args.path, delete=args.delete, append=args.append)
    elif args.subcommand == "unuse":
        unuse_path(args.path)
    elif args.subcommand == "swap":
        swap_modules(args.first, args.second)
    elif args.subcommand == "refresh":
        refresh_modules()
    elif args.subcommand == "collection":
        collection(args.c_command, args)
    elif args.subcommand == "clone":
        clone(args.c_command, args)
    elif args.subcommand == "reset":
        reset()
    elif args.subcommand == "init":
        init(args.modulepath)
    elif args.subcommand == "cache":
        cache(args.c_command)
    elif args.subcommand == "test":
        test(args, unknown_args)
    else:
        parser.error("missing required subcommand")


def main(argv=None):
    argv = argv or sys.argv[1:]
    parser = argument_parser(prog="module")
    setup_parser(parser)
    args, unknown_args = parser.parse_known_args()

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
        shell.set_shell(args.shell)

    if args.dryrun:
        config.set("dryrun", True)

    if args.debug:
        config.set("debug", True)

    try:
        main2(parser, args, unknown_args)
    except Exception as e:
        print("HERE I AM", config.get("debug"))
        if config.get("debug"):
            raise
        xio.die(str(e))
    except KeyboardInterrupt:
        sys.stderr.write("\n")
        xio.die("Keyboard interrupt.")
    except SystemExit as e:
        return e.code


if __name__ == "__main__":
    sys.exit(main())
