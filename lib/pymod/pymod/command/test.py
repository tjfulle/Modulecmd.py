import os
import re
import sys
import argparse
import pytest
from six import StringIO

from llnl.util.filesystem import working_dir
from llnl.util.tty.colify import colify
from contrib.util.tty import redirect_stdout2 as redirect_stdout

import pymod.paths
import pymod.modulepath

description = "run pymod's unit tests"
section = "developer"
level = "long"


def setup_parser(subparser):
    subparser.add_argument(
        "-H",
        "--pytest-help",
        action="store_true",
        default=False,
        help="print full pytest help message, showing advanced options",
    )

    list_group = subparser.add_mutually_exclusive_group()
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
    subparser.add_argument(
        "tests",
        nargs=argparse.REMAINDER,
        help="list of tests to run (will be passed to pytest -k)",
    )


def do_list(args, unknown_args):
    """Print a lists of tests than what pytest offers."""
    # Run test collection and get the tree out.
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
        colify(output_lines)


def test(parser, args, unknown_args):
    if args.pytest_help:
        # make the pytest.main help output more accurate
        with redirect_stdout():
            sys.argv[0] = "pymod test"
            pytest.main(["-h"])
        return

    pytest_root = pymod.paths.test_path

    # pytest.ini lives in the root of the pymod repository.
    with redirect_stdout():
        with working_dir(pytest_root):
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
