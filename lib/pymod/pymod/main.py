"""This is the implementation of the module command line executable.

In a normal Modulecmd.py installation, this is invoked from a shell function
evaluating the bin/module script after the system path is set up.
"""
from __future__ import print_function

import re
import os
import sys
import inspect
import pstats
import argparse
from six import StringIO


import pymod.paths
import pymod.config
import pymod.modulepath
import pymod.environ
import pymod.command
import pymod.shell

import llnl.util.tty as tty
import llnl.util.tty.color as color
from llnl.util.tty.log import log_output
from contrib.util.tty import redirect_stdout


#: names of profile statistics
stat_names = pstats.Stats.sort_arg_dict_default

#: top-level aliases for pymod commands
aliases = {
    'av': 'avail',
    'add': 'load',
    'ls': 'list',
    'rm': 'unload',
    'which': 'find',
    'cn': 'collection',
}

#: help levels in order of detail (i.e., number of commands shown)
levels = ['short', 'long']

#: intro text for help at different levels
intro_by_level = {
    'short': 'These are common pymod commands:',
    'long':  'Complete list of pymod commands:',
}

#: control top-level pymod options shown in basic vs. advanced help
options_by_level = {
    'short': ['h', 'V', 'color', 'dryrun'],
    'long': 'all'
}

#: Longer text for each section, to show in help
section_descriptions = {
    'info':        'informational',
    'basic':       'modify environment',
    'developer':   'developer',
    'modulepath':  'modulepath',
    'collections': 'collections',
    'clones':      'clones',
    'help':        'more help',
}

#: preferential command order for some sections (e.g., build pipeline is
#: in execution order, not alphabetical)
section_order = {
    'info': ['avail', 'list', 'whatis', 'show', 'cat', 'more', 'find'],
    'basic': ['load', 'unload', 'reload', 'swap', 'purge', 'refresh'],
    'modulepath': ['path', 'use', 'unuse'],
    'collections': ['save', 'restore'],
    'clones': ['save', 'restore', 'remove',],
}

#: Properties that commands are required to set.
required_command_properties = ['level', 'description']

#: Recorded directory where module command was originally invoked
pymod_working_dir = None


def set_working_dir():
    """Change the working directory to getcwd, or pymod prefix if no cwd."""
    global pymod_working_dir
    try:
        pymod_working_dir = os.getcwd()
    except OSError:
        os.chdir(pymod.paths.prefix)
        pymod_working_dir = pymod.paths.prefix


def add_all_commands(parser):
    """Add all pymod subcommands to the parser."""
    for command in pymod.command.all_commands():
        parser.add_command(command)


def index_commands():
    """create an index of commands by section for this help level"""
    index = {}
    for command in pymod.command.all_commands():
        cmd_module = pymod.command.get_module(command)

        # make sure command modules have required properties
        for p in required_command_properties:
            prop = getattr(cmd_module, p, None)
            if not prop:
                tty.die('Command doesn\'t define a property {0!r}: {1}'
                            .format(p, command))

        # add commands to lists for their level and higher levels
        for level in reversed(levels):
            level_sections = index.setdefault(level, {})
            commands = level_sections.setdefault(cmd_module.section, [])
            commands.append(command)
            if level == cmd_module.level:
                break

    return index


class PymodHelpFormatter(argparse.RawTextHelpFormatter):
    def _format_actions_usage(self, actions, groups):
        """Formatter with more concise usage strings."""
        usage = super(
            PymodHelpFormatter, self)._format_actions_usage(actions, groups)

        # compress single-character flags that are not mutually exclusive
        # at the beginning of the usage string
        chars = ''.join(re.findall(r'\[-(.)\]', usage))
        usage = re.sub(r'\[-.\] ?', '', usage)
        if chars:
            return '[-%s] %s' % (chars, usage)
        else:
            return usage


class PymodArgumentParser(argparse.ArgumentParser):

    def _print_message(self, message, file=None):
        if message:
            if file is None:
                file = sys.stderr
            file.write(message)

    def format_help_sections(self, level):
        """Format help on sections for a particular verbosity level.

        Parameters
        ----------
        level : str
            'short' or 'long' (more commands shown for long)
        """
        if level not in levels:
            raise ValueError("level must be one of: %s" % levels)

        # lazily add all commands to the parser when needed.
        add_all_commands(self)

        """Print help on subcommands in neatly formatted sections."""
        formatter = self._get_formatter()

        # Create a list of subcommand actions. Argparse internals are nasty!
        # Note: you can only call _get_subactions() once.  Even nastier!
        if not hasattr(self, 'actions'):
            self.actions = self._subparsers._actions[-1]._get_subactions()

        # make a set of commands not yet added.
        remaining = set(pymod.command.all_commands())

        def add_group(group):
            formatter.start_section(group.title)
            formatter.add_text(group.description)
            formatter.add_arguments(group._group_actions)
            formatter.end_section()

        def add_subcommand_group(title, commands):
            """Add informational help group for a specific subcommand set."""
            cmd_set = set(c for c in commands)

            # make a dict of commands of interest
            cmds = dict((a.dest, a) for a in self.actions
                        if a.dest in cmd_set)

            # add commands to a group in order, and add the group
            group = argparse._ArgumentGroup(self, title=title)
            for name in commands:
                group._add_action(cmds[name])
                if name in remaining:
                    remaining.remove(name)
            add_group(group)

        # select only the options for the particular level we're showing.
        show_options = options_by_level[level]
        if show_options != 'all':
            opts = dict((opt.option_strings[0].strip('-'), opt)
                        for opt in self._optionals._group_actions)

            new_actions = [opts[letter] for letter in show_options]
            self._optionals._group_actions = new_actions

        # custom, more concise usage for top level
        help_options = self._optionals._group_actions
        help_options = help_options + [self._positionals._group_actions[-1]]
        formatter.add_usage(
            self.usage, help_options, self._mutually_exclusive_groups)

        # description
        formatter.add_text(self.description)

        # start subcommands
        formatter.add_text(intro_by_level[level])

        # add argument groups based on metadata in commands
        index = index_commands()
        sections = index[level]

        for section in sorted(sections):
            if section == 'help':
                continue   # Cover help in the epilog.

            group_description = section_descriptions.get(section, section)

            to_display = sections[section]
            commands = []

            # add commands whose order we care about first.
            if section in section_order:
                commands.extend(cmd for cmd in section_order[section]
                                if cmd in to_display)

            # add rest in alphabetical order.
            commands.extend(cmd for cmd in sorted(sections[section])
                            if cmd not in commands)

            # add the group to the parser
            add_subcommand_group(group_description, commands)

        # optionals
        add_group(self._optionals)

        # epilog
        formatter.add_text("""\
{help}:
  module help --all       list all commands and options
  module help <command>   help on a specific command"""
.format(help=section_descriptions['help']))

        # determine help from format above
        return formatter.format_help()

    def add_subparsers(self, **kwargs):
        """Ensure that sensible defaults are propagated to subparsers"""
        kwargs.setdefault('metavar', 'SUBCOMMAND')
        sp = super(PymodArgumentParser, self).add_subparsers(**kwargs)
        old_add_parser = sp.add_parser

        def add_parser(name, **kwargs):
            kwargs.setdefault('formatter_class', PymodHelpFormatter)
            return old_add_parser(name, **kwargs)
        sp.add_parser = add_parser
        return sp

    def add_command(self, cmd_name):
        """Add one subcommand to this parser."""
        # lazily initialize any subparsers
        if not hasattr(self, 'subparsers'):
            # remove the "shell" and the dummy "command" argument.
            if self._actions[-1].dest == 'command':
                self._remove_action(self._actions[-1])
            self.subparsers = self.add_subparsers(metavar='COMMAND',
                                                  dest="command")

        # each command module implements a parser() function, to which we
        # pass its subparser for setup.
        module = pymod.command.get_module(cmd_name)

        # build a list of aliases
        alias_list = [k for k, v in aliases.items() if v == cmd_name]

        subparser = self.subparsers.add_parser(
            cmd_name, aliases=alias_list,
            help=module.description, description=module.description)
        module.setup_parser(subparser)

        # return the callable function for the command
        return pymod.command.get_command(cmd_name)

    def format_help(self, level='short'):
        if self.prog in ('pymod', 'modulecmd.py'):
            # use format_help_sections for the main pymod parser, but not
            # for subparsers
            return self.format_help_sections(level)
        else:
            # in subparsers, self.prog is, e.g., 'modulecmd.py load'
            return super(PymodArgumentParser, self).format_help()


def make_argument_parser(**kwargs):
    """Create an basic argument parser without any subcommands added."""
    parser = PymodArgumentParser(
        formatter_class=PymodHelpFormatter, add_help=False,
        description=(
            'pymod - Environment modules framework implemented in Python\n\n'
            'Environment modules, or just modules, are files containing commands that,\n'
            'when processed by the module Framework, modify the current shell\'s\n'
            'environment.  Modules allow users to dynamically modify their environment.\n'
            'This, python, implementation of an environment module framework is inspired\n'
            'by existing frameworks written in C/TCL and Lua and seeks parity with the\n'
            'original TCL environment modules.'),
        **kwargs)

    parser.add_argument(
        '-h', '--help',
        dest='help', action='store_const', const='short', default=None,
        help="show this help message and exit")
    parser.add_argument(
        '-H', '--all-help',
        dest='help', action='store_const', const='long', default=None,
        help="show help for all commands (same as pymod help --all)")
    parser.add_argument(
        '--time', action='store_true', default=False,
        help='time execution of command')
    parser.add_argument(
        '--verbose', action='store_true', default=False,
        help='print additional output')
    parser.add_argument(
        '--debug', action='store_true', default=False,
        help='run additional debug checks')
    parser.add_argument(
        '--dryrun', action='store_true', default=False,
        help='print commands to console, but do not execute them')
    parser.add_argument(
        '--pdb', action='store_true', default=False,
        help='run execution through pdb debugger')
    parser.add_argument(
        '--trace', action='store_true', default=False,
        help='trace execution of command')
    parser.add_argument(
        '-V', '--version', action='store_true',
        help='show version number and exit')
    parser.add_argument(
        '-m', '--mock', action='store_true',
        help='use mock modulepath instead of real one')
    parser.add_argument(
        '--color', action='store', default='auto',
        choices=('always', 'never', 'auto'),
        help="when to colorize output (default: auto)")

    return parser


class PymodCommand(object):
    """Callable object that invokes a pymod command (for testing).

    Example usage::

        load = PymodCommand('load')
        load('module')

    Use this to invoke pymod commands directly from Python and check
    their output.
    """
    def __init__(self, command_name):
        """Create a new PymodCommand that invokes ``command_name`` when called.

        Args:
            command_name (str): name of the command to invoke
        """
        self.parser = make_argument_parser()
        self.command = self.parser.add_command(command_name)
        self.command_name = command_name

    def __call__(self, *argv, **kwargs):
        """Invoke this PymodCommand.

        Args:
            argv (list of str): command line arguments.

        Keyword Args:
            fail_on_error (optional bool): Don't raise an exception on error

        Returns:
            (str): combined output and error as a string

        On return, if ``fail_on_error`` is False, return value of command
        is set in ``returncode`` property, and the error is set in the
        ``error`` property.  Otherwise, raise an error.
        """
        # set these before every call to clear them out
        self.returncode = None
        self.error = None

        args, unknown = self.parser.parse_known_args(
            [self.command_name] + list(argv))

        fail_on_error = kwargs.get('fail_on_error', True)

        out = StringIO()
        try:
            with log_output(out):
                self.returncode = _invoke_command(
                    self.command, self.parser, args, unknown)

        except SystemExit as e:
            self.returncode = e.code

        except BaseException as e:
            self.error = e
            if fail_on_error:
                raise

        if fail_on_error and self.returncode not in (None, 0):
            raise PymodCommandError(
                "Command exited with code %d: %s(%s)" % (
                    self.returncode, self.command_name,
                    ', '.join("'%s'" % a for a in argv)))

        return out.getvalue()


def setup_main_options(args):
    """Configure pymod globals based on the basic options."""
    # Set up environment based on args.
    tty.set_verbose(args.verbose)
    tty.set_debug(args.debug)
#    tty.set_trace(args.trace)

    # debug must be set first so that it can even affect behvaior of
    # errors raised by pymod.config.
    if args.debug:
        # pymod.error.debug = True
        pymod.config.set('debug', True, scope='command_line')

    if args.dryrun:
        pymod.config.set('dryrun', True, scope='command_line')

    if args.mock:
        path = os.path.join(pymod.paths.mock_modulepath, 'core')
        p = pymod.modulepath.ModulePath([path])
        pymod.modulepath.set_path(p)

    if args.shell != pymod.config.get('default_shell'):
        pymod.shell.set_shell(args.shell)

    # when to use color (takes always, auto, or never)
    color.set_color_when(args.color)


def allows_unknown_args(command):
    """Implements really simple argument injection for unknown arguments.

    Commands may add an optional argument called "unknown args" to
    indicate they can handle unknonwn args, and we'll pass the unknown
    args in.
    """
    info = dict(inspect.getmembers(command))
    varnames = info['__code__'].co_varnames
    argcount = info['__code__'].co_argcount
    return (argcount == 3 and varnames[2] == 'unknown_args')


def _invoke_command(command, parser, args, unknown_args):
    """Run a pymod command *without* setting pymod global options."""
    if allows_unknown_args(command):
        return_val = command(parser, args, unknown_args)
    else:
        if unknown_args:
            tty.die('unrecognized arguments: {}'
                        .format(' '.join(unknown_args)))
        return_val = command(parser, args)

    # Allow commands to return and error code if they want
    return 0 if return_val is None else return_val


def main(argv=None):
    """This is the entry point for the pymod command.

    Parameters
    ----------
    argv : list of str or None
        command line arguments, NOT including the executable name. If None,
        parses from sys.argv.
    """

    # Pull out the shell from argv
    argv = argv or sys.argv[1:]
    assert len(argv) >= 1
    shell = argv.pop(0)
    shells = ('bash', 'csh', 'python')
    if shell not in shells:
        raise ValueError('shell argument must by one of {0}'.format(shells))

    # Create a parser with a simple positional argument first.  We'll
    # lazily load the subcommand(s) we need later. This allows us to
    # avoid loading all the modules from pymod.command when we don't need
    # them, which reduces startup latency.
    parser = make_argument_parser()
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args, unknown = parser.parse_known_args(argv)
    args.shell = shell

    # Just print help and exit if run with no arguments at all
    no_args = len(argv) == 0
    if no_args:
        with redirect_stdout():
            parser.print_help()
        return 1

    # -h, -H, and -V are special as they do not require a command, but
    # all the other options do nothing without a command.
    if args.version:
        sys.stderr.write(str(pymod.pymod_version) + '\n')
        return 0
    elif args.help:
        message = parser.format_help(level=args.help)
        with redirect_stdout():
            sys.stderr.write(message)
        return 0
    elif not args.command:
        with redirect_stdout():
            parser.print_help()
        return 1

    try:
        # ensure options on pymod command come before everything
        setup_main_options(args)

        # Try to load the particular command the caller asked for.  If there
        # is no module for it, just die.
        cmd_name = args.command[0]
        cmd_name = aliases.get(cmd_name, cmd_name)

        try:
            command = parser.add_command(cmd_name)
        except ImportError:
           # if pymod.config.get('config:debug'):
           #     raise
            tty.die("Unknown command: %s" % args.command[0])

        # Re-parse with the proper sub-parser added.
        args, unknown = parser.parse_known_args(argv)

        # many operations will fail without a working directory.
        set_working_dir()

        # now we can actually execute the command.
        if args.pdb:
            import pdb
            pdb.runctx('_invoke_command(command, parser, args, unknown)',
                       globals(), locals())
            return 0
        else:
            return _invoke_command(command, parser, args, unknown)

    except Exception as e:
        if pymod.config.get('debug'):
            raise
        tty.die(str(e))

    except KeyboardInterrupt:
        sys.stderr.write('\n')
        tty.die("Keyboard interrupt.")

    except SystemExit as e:
        return e.code


class PymodCommandError(Exception):
    """Raised when PymodCommand execution fails."""
