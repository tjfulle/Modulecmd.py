from __future__ import print_function

import os
import re
import sys
import argparse

import llnl.util.tty as tty
from llnl.util.tty.colify import colify
from llnl.util.argparsewriter import ArgparseWriter, ArgparseRstWriter

import pymod.main
from pymod.main import section_descriptions


description = "list available Modulecmd.py commands"
section = "developer"
level = "long"


#: list of command formatters
formatters = {}


def formatter(func):
    """Decorator used to register formatters"""
    formatters[func.__name__] = func
    return func


def setup_parser(subparser):
    subparser.add_argument(
        '--format', default='names', choices=formatters,
        help='format to be used to print the output (default: names)')
    subparser.add_argument(
        '--header', metavar='FILE', default=None, action='store',
        help='prepend contents of FILE to the output (useful for rst format)')
    subparser.add_argument(
        '--update', metavar='FILE', default=None, action='store',
        help='write output to the specified file, if any command is newer')
    subparser.add_argument(
        'rst_files', nargs=argparse.REMAINDER,
        help='list of rst files to search for `_cmd-module-<cmd>` cross-refs')


class PymodArgparseRstWriter(ArgparseRstWriter):
    """RST writer tailored for Modulecmd.py documentation."""

    def __init__(self, documented_commands, out=sys.stderr):
        super(PymodArgparseRstWriter, self).__init__(out)
        self.documented = documented_commands if documented_commands else []

    def usage(self, *args):
        super(PymodArgparseRstWriter, self).usage(*args)
        command = re.sub(' ', '-', self.parser.prog)
        if command in self.documented:  # pragma: no cover
            self.line()
            self.line(':ref:`More documentation <cmd-%s>`' % command)


class SubcommandWriter(ArgparseWriter):
    def begin_command(self, prog):
        self.out.write('    ' * self.level + prog)
        self.out.write('\n')


@formatter
def subcommands(args, out):
    parser = pymod.main.make_argument_parser()
    pymod.main.add_all_commands(parser)
    SubcommandWriter(out).write(parser)


def rst_index(out=sys.stderr):
    out.write('\n')

    index = pymod.main.index_commands()
    sections = index['long']

    dmax = max(len(section_descriptions.get(s, s)) for s in sections) + 2
    cmax = max(len(c) for _, c in sections.items()) + 60

    row = "%s  %s\n" % ('=' * dmax, '=' * cmax)
    line = '%%-%ds  %%s\n' % dmax

    out.write(row)
    out.write(line % (" Category ", " Commands "))
    out.write(row)
    for section, commands in sorted(sections.items()):
        description = section_descriptions.get(section, section)

        for i, command in enumerate(sorted(commands)):
            description = description.capitalize() if i == 0 else ''
            ref = ':ref:`%s <pymod-%s>`' % (command, command)
            comma = ',' if i != len(commands) - 1 else ''
            bar = '| ' if i % 8 == 0 else '  '
            out.write(line % (description, bar + ref + comma))
    out.write(row)


@formatter
def rst(args, out):
    # create a parser with all commands
    parser = pymod.main.make_argument_parser()
    pymod.main.add_all_commands(parser)

    # extract cross-refs of the form `_cmd-pymod-<cmd>:` from rst files
    documented_commands = set()
    for filename in args.rst_files:  # pragma: no cover
        with open(filename) as f:
            for line in f:
                match = re.match(r'\.\. _cmd-(pymod-.*):', line)
                if match:
                    documented_commands.add(match.group(1).strip())

    # print an index to each command
    rst_index(out)
    out.write('\n')

    # print sections for each command and subcommand
    PymodArgparseRstWriter(documented_commands, out).write(parser, root=1)


@formatter
def names(args, out):
    colify(pymod.command.all_commands(), output=out)


def prepend_header(args, out):  # pragma: no cover
    if not args.header:
        return

    with open(args.header) as header:
        out.write(header.read())


def commands(parser, args):

    # Print to stderr
    formatter = formatters[args.format]

     # check header first so we don't open out files unnecessarily
    if args.header and not os.path.exists(args.header):  # pragma: no cover
        tty.die("No such file: '%s'" % args.header)

    # if we're updating an existing file, only write output if a command
    # is newer than the file.
    if args.update:  # pragma: no cover
        if os.path.exists(args.update):
            files = [
                pymod.command.get_module(command).__file__.rstrip('c')  # pyc -> py
                for command in pymod.command.all_commands()]
            last_update = os.path.getmtime(args.update)
            if not any(os.path.getmtime(f) > last_update for f in files):
                tty.msg('File is up to date: %s' % args.update)
                return

        tty.msg('Updating file: %s' % args.update)
        with open(args.update, 'w') as f:
            prepend_header(args, f)
            formatter(args, f)

    else:
        prepend_header(args, sys.stderr)
        formatter(args, sys.stderr)
