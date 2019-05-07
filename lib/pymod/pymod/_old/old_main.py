#!/usr/bin/env python
from __future__ import division, print_function
import os
import sys
import time
import atexit
import argparse

from . import defaults
from .constants import *
from .config import cfg
from .color import colorize
from .trace import trace
from .pager import pager
from .shell import get_shell
from .utils import split, total_module_time
from .tty import write_to_console, tty
from .instruction_logger import InstructionLogger
from .controller import MasterController
from .optparse import ModuleOptionParser


usage = 'module [--version] [-h|--help] [--profile] [--time] <command> [<args>]'
help_page = """\

{B}NAME{b}

{sp}module - Environment modules framework implemented in Python

{B}SYNOPSIS{b}

{sp}{usage}

{B}DESCRIPTION{b}

{sp}Environment modules, or just modules, are files containing commands that,
{sp}when processed by the module Framework, modify the current shell's
{sp}environment.  Modules allow users to dynamically modify their environment.
{sp}This, python, implementation of an environment module framework is inspired
{sp}by existing frameworks written in C/TCL and Lua and seeks parity with the
{sp}original TCL environment modules.

{B}OPTIONS{b}

{sp}--version
{dp}Show program's version number and exit.
{sp}--help
{dp}If a module command is named, shows the help message for that command,
{dp}otherwise, show this help message and exit.
{sp}--profile
{dp}Run command in Python profiler.
{sp}--time
{dp}Time the module execution.

{B}MODULE COMMANDS{b}

{sp}avail [regex] [--terse] ['-F']
{dp}Displays available modules.  {U}regex{u} is a regular expression highlighted
{dp}in the output.

{dp}With the {U}--terse{u} option, output will be displayed in terse format.

{dp}With the {U}-F{u} option, full output will be displayed, including nonexistent
{dp}and empty directories.

{sp}cat <name>
{dp}print {U}name{u} to the console output.  {U}name{u} can be the name of a
{dp}module, collection, or one of {I}avail{i} or {I}collections{i}.

{sp}edit <name>
{dp}Open module {U}name{u}'s file in EDITOR for editing.

{sp}file <module> [module...]
{dp}Show the file path[s] to {U}module [...]{u}.

{sp}init [--mp=MP]
{dp}Initialize the module command.  This command is a shortcut for calling

{dp}{sp}module use <PATH1>
{dp}{sp}module use <PATH2>
{dp}{sp}...
{dp}{sp}module use <PATHN>
{dp}{sp}module restore default

{sp}list (l) [regex] [--terse] [--show-command] [-c]
{dp}Displays loaded modules.  {U}regex{u} is a regular expression highlighted
{dp}in the output.

{dp}With the {U}--terse{u} option, output is displayed in terse format.
{dp}With the {U}--show-command{u} or {U}-c{u} option, output displays load commands

{sp}load (add) <name> [name...] [-x] [--insert-at <i>] [options]
{sp}unload (rm) <name> [name...]
{sp}reload <name> [name...]
{dp}Load, unload, or reload the module[s] {U}name [name...]{u}

{dp}With the {U}-x{u} option, the module will not be added to the list of loaded modules.

{dp}With the {U}--insert-at <i>{u} option, the module will be loaded as the {I}i{i}th module.

{dp}Additional options can be sent directly to the module using the syntax,
{dp}{U}+option[=value]{u}.  See the section on module options for more details.

{sp}more <name>
{dp}print {U}name{u} to the console output on page at a time.  Allows movement
{dp}through files similar to shell's {I}less{i} program.  {U}name{i} can be the name
{dp}of a module, collection, or one of {I}avail{i} or {I}collections{i}.

{sp}path
{dp}Show the module path

{sp}purge [-F]
{dp}Unload all loaded modules

{dp}With the {U}-F{u} option, no modules will be loaded after purging, even if the variable
{dp}load_after_purge is set in the rc file.

{sp}refresh
{dp}Refresh (unload/reload) all modules

{sp}show <name> [name...]
{dp}Show the commands in the module file[s].

{sp}swap <name_a> <name_b>
{dp}Unload module {U}name_a{u} and load {U}name_b{u} in its place

{dp}With the {U}-D{u} option, {I}use{i} behaves exactly as {I}unuse{i}.

{sp}whatis
{dp}Display module whatis string.  The whatis string is a short informational
{dp}message a module can provide.  If not defined by the module, a default is
{dp}displayed.

{B}MODULE COLLECTION COMMANDS{b}

{sp}collection save [name|-f name]
{sp}collection restore <name>
{sp}collection avail
{sp}collection show <name>
{sp}collection rm <name>
{dp}Save, restore, list, display, or remove a collection of modules.

{dp}Module collections are collections of modules that can be restored (loaded)
{dp}with a single command.

{dp}The subcommand {I}save{i} saves the currently loaded modules to the collection
{dp} {U}name{u}, if {U}name{u} is supplied; if {U}-f name{u} is supplied, the collection
{dp}is saved to a file named {U}name{u}.collection in the current working directory;
{dp}otherwise, the modules are saved to the {dp}user's default collection.

{dp}{I}restore{i} loads the modules saved to collection {U}name{u} after unloading
{dp}any loaded modules.  If {U}name{u} is not supplied, the user's default
{dp}collection is restored.  If {U}name{u} is a file, the collection is loaded from
{dp}the file.

{dp}{I}avail{i} lists saved collections.

{dp}{I}show{i} shows the contents of the module collection {U}name{u}.

{dp}{I}rm{i} removes collection {U}name{u} from the list of collections.

{B}MODULE CLONE COMMANDS{b}

{sp}clone save <name>
{sp}clone restore <name>
{sp}clone avail
{sp}clone rm <name>
{dp}Save, restore, list, display, or remove a clone of the environment.

{B}MODULE COMMANDS THAT MODIFY THE ENVIRONMENT DIRECTLY{b}
Shell aliases and environment variables can be set directly by module.

{sp}shell alias [name[=value]]
{sp}shell alias -D <name>
{dp}List, create, remove shell aliases.  Shell aliases allow a string to be
{dp}substituted for shell commands.

{dp}If arguments are supplied, an {I}shell alias{i} is defined for the {U}name{u} whose
{dp}{U}value{u} is given.  If no {U}value{u} is given, {I}shell alias{i} will print
{dp}the current value of the alias.

{dp}Without arguments, {I}shell alias{i} prints the list of a shell aliases.

{dp}With the {U}-D{u} option, {U}name{u} will be deleted from the list of defined
{dp}aliases.

{sp}shell env <name[=value]>
{sp}shell env -D <name>
{dp}List, create, remove environment variables.

{dp}{I}shell env{i}: An environment variable is defined for the {U}name{u} whose
{dp}{U}value{u}
{dp}is given.  If no {U}value{u} is given, {I}shell env{i} will print the current
{dp}value of the environment variable.

{dp}With the {U}-D{u} option, {U}name{u} will be unset from the environment.

{B}USER ENVIRONMENT FILE{b}

The user environment file PYMOD_DOT_DIR/module.env is used to configure the
behavior of pymod on a per-user basis.  The pymod environment file uses Python
syntax.

The following parameters are read from the environment file:

The environment file is imported by pymod and is made available to modules
executed by pymod as the 'user_env' object.  e.g., if the function 'baz' were
defined in a users module.env file, that function would be available as
'user_env.baz' in any module executed by pymod.

{B}ENVIRONMENT VARIABLES{b}

pymod uses the following environment variables:

LOADEDMODULES
{sp}A colon separated list of all loaded modulefiles.

MODULEPATH
{sp}The path that the module command searches when looking for modulefiles.
{sp}MODULEPATH can be set directly in a shell startup script or using {I}module use{i}.

_LMFILES_
{sp}A colon separated list of the full pathname for all loaded modulefiles.

_LMOPTS_
{sp}A list of set options for all loaded modules.

_LMREFCNT_<PATH>
{sp}A reference count for all path-like variables.

PYMOD_DOT_DIR
{sp}If the PYMOD_DOT_DIR environment variable is set then it specifies a path to
{sp}use instead of the default (~/.pymod).  PYMOD_DOT_DIR is used by pymod to
{sp}write internally used data.  It is also the directory where the user
{sp}environment file is looked for.

{B}MODULEFILES{b}

pymod module files are python files that are executed by the pymod Framework.
Modulefiles must have a .py file extension and be on the MODULEPATH to be
recognized.  pymod executes module files in an environment providing the
following commands:

{U}GENERAL PURPOSE{u}
{sp}{I}getenv(name){i}
{dp}Get the value of environment variable given by name.  Returns None if name
{dp}is not defined.
{sp}{I}get_hostname(){i}
{dp}Get the value of the host name of the sytem.
{sp}{I}mode(){i}
{dp}Return the active mode.  One of "load" or "unload"
{sp}{I}self{i}
{dp}Reference to this modules object.
{sp}{I}HOME{i}
{dp}The path to HOME
{sp}{I}USER{i}
{dp}The name of USER
{sp}{I}IS_DARWIN{i}
{dp}Boolean.  True if the system is Darwin.  False otherwise.
{sp}{I}user_env{i}
{dp}Reference to a user defined Python module containing custom commands.
{sp}{I}args{i}
{dp}List of commands passed from command line to this module.

{U}MESSAGE LOGGING{u}
{sp}{I}log_message(message){i}
{dp}Log an informational message to the console.
{sp}{I}log_info(message){i}
{dp}Log an informational message to the console.
{sp}{I}log_warning(message){i}
{dp}Log a warning message to the console.
{sp}{I}log_error(message){i}
{dp}Log an error message to the console and quit.

{U}ENVIRONMENT MODIFICATION{u}
{sp}{I}setenv(variable, value){i}
{dp}Set the environment variable variable to value.
{sp}{I}unsetenv(variable){i}
{dp}Unset the environment variable variable.
{sp}{I}set_alias(name, value){i}
{dp}Set the alias name to value.
{sp}{I}unset_alias(name){i}
{dp}Unset the alias given by name.

{sp}{I}set_shell_function(name, value){i}
{dp}Set the shell function name to value.
{sp}{I}unset_shell_function(name, value){i}
{dp}Unset the shell function name

{sp}{I}prepend_path(pathname, value){i}
{dp}Prepend value to path-like variable pathname.
{sp}{I}append_path(pathname, value){i}
{dp}Append value to path-like variable pathname.
{sp}{I}remove_path(pathname, value){i}
{dp}Remove value from path-like variable pathname.

{U}INTERACTION WITH OTHER MODULES{u}
{sp}{I}prereq(name){i}
{dp}Module name is a prerequisite of this module.
{dp}If name is not loaded, pymod will quit.
{sp}{I}prereq_any(*names){i}
{dp}Any one of names is a prerequisite of this module.
{dp}If none of names is not loaded, pymod will quit.
{sp}{I}conflict(*names){i}
{dp}Module name is a prerequisite of this module.
{dp}If name is not loaded, pymod will quit.
{sp}{I}load(name){i}
{dp}Load the module name.
{sp}{I}load_first(*names){i}
{dp}Load the first module in names.
{sp}{I}unload(name){i}
{dp}Unload the module name.

{U}MODULE OPTIONS{u}
A module can support command line options.  Options are specified on the
commandline as

{dp}{I}module load <modulename> [+option[=value] [+option...]]{i}

The following modulefile functions register options

{sp}{I}add_option(name, action='store_true'){i}
{dp}Register a module option.  By default, options are boolean flags.  Pass
{dp}{I}action='store'{i} to register an option that takes a value.

{sp}{I}add_mutually_exclusive_option(name1, name2, action='store_true'){i}
{dp}Register a mutually exclusive option

{sp}{I}parse_opts{i}
{dp}Parse module options.  Only options added before calling {I}parse_opts{i} will
{dp}be parsed.

{I}EXAMPLE{i}
To specify two options for module 'spam', in modulefile spam.py do

{sp}add_option('+x', action='store')  # option with value
{sp}add_option('+b')  # boolean option
{sp}opts = parse_opts()

{sp}if (opts.b):
{sp}    # Do something
{sp}if (opts.x == 'baz'):
{sp}    # Do something

On the commandline, the module spam can be loaded as

{sp}{I}module load spam +b +x=baz{i}

{U}OTHER COMMANDS{u}
{sp}{I}family(name){i}
{dp}Set the name of the module's family.
{sp}{I}execute(command){i}
{dp}Execute command in the current shell.
{sp}{I}whatis(string){i}
{dp}Store string as an informational message describing this module.

{U}EXAMPLE{u}
The following commands, when put in a module file on MODULEPATH, prepends the
user's bin directory to the PATH and aliases the ls command.

{sp}prepend_path('PATH', '~/bin')
{sp}set_alias('ls', 'ls -lF')

""".format(sp=' '*3, dp=' '*6, tp=' '*9,
           B='\033[1m',  # bold
           b='\033[0m',  # turn off bold
           U='\033[4m',  # underline
           u='\033[0m',  # turn off underline
           I='\033[3m',  # italic
           i='\033[0m',  # turn off italic
           N='\033[0m',
           usage=usage)


def get_argv(argv):

    if argv is None:
        argv = sys.argv[1:]

    if len(argv) < 2:
        return argv

    aliases = {'add': [LOAD],
               RM: [UNLOAD],
               'av': [AVAIL],
               'l': [LIST],
               'ls': [LIST],
               'ac': [COLLECTION, AVAIL],
               'describe': [COLLECTION, SHOW],
               SAVE: [COLLECTION, SAVE],
               'saverm': [COLLECTION, RM],
               'rmc': [COLLECTION, RM],
               'savelist': [COLLECTION, AVAIL],
               RESTORE: [COLLECTION, RESTORE],
               'coll': [COLLECTION],
               }

    if argv[1] not in aliases:
        return argv

    shell = argv[0:1]
    command = aliases[argv[1]]
    remainder = argv[2:]

    return shell + command + remainder


@trace
def main(argv=None):
    """The main module interface"""
    from argparse import ArgumentParser, SUPPRESS
    argv = get_argv(argv)

    description = """Python modules framework.  See 'module help' for more
    detailed help"""

    pp = ArgumentParser(add_help=False)

    ax, axo, mx = 'argv', 'argvo', 'modulename'
    p1 = ArgumentParser(prog='module', usage=usage, description=description)
    p1.add_argument('--time', action='store_true', default=False)
    p1.add_argument('--verbosity', '-v', action='count', default=None)
    p1.add_argument('--debug', action='store_true', default=False)
    p1.add_argument('--version', action='version', version='%(prog)s '+version)

    p1.add_argument(SHELL, choices=('bash', 'csh', 'python'), help=SUPPRESS)

    sub_p = p1.add_subparsers(dest='subparser', title='subcommands')

    p = sub_p.add_parser(ALIAS, parents=[pp], help='List or set a module alias')
    p.add_argument('arg', nargs='?',
                   help='If given, name of module alias to list or module '
                        'aliases to set, specified as name=value.  If not '
                        'supplied, list all module aliases')
    p.add_argument('-D', action='store_true', help='Delete alias')

    p = sub_p.add_parser(AVAIL, parents=[pp], help='Display available modules')
    p.add_argument('regex', nargs='?', metavar='regex',
                   help='Highlight available modules matching "regex"')
    p.add_argument('-t', '--terse', default=False, action='store_true',
                   help='Display output in terse format [default: %(default)s]')
    p.add_argument('-F', default=False, action='store_true',
                   help='Display full output [default: %(default)s]')

    p = sub_p.add_parser(EDIT, parents=[pp], help='Edit module file[s] in EDITOR')
    p.add_argument(ax, nargs='+', metavar=mx, help='Valid module name[s]')

    p = sub_p.add_parser(FILE, parents=[pp], help='Show path to module file')
    p.add_argument(ax, nargs='+', metavar=mx, help='Valid module name[s]')

    p = sub_p.add_parser(HELP, parents=[pp],
                         help='Display the detailed module help page')
    p.add_argument(ax, nargs='*', metavar=mx, help='Valid module names')

    p = sub_p.add_parser(INIT, parents=[pp], help='Initialize modulecmd')
    p.add_argument('--mp', help='Modulepath', default=os.getenv('MODULEPATH', ''))

    p = sub_p.add_parser(LIST, parents=[pp], help='Display loaded modules')
    p.add_argument('regex', nargs='?', metavar='regex',
                   help='Highlight loaded modules matching "regex"')
    p.add_argument('-t', '--terse', default=False, action='store_true',
                   help='Display output in terse format [default: %(default)s]')
    p.add_argument('-c', '--show-command', default=False, action='store_true',
                   help='Display output in show command format [default: %(default)s]')

    p = sub_p.add_parser(LOAD, parents=[pp], help='Load module[s]')
    p.add_argument('--dryrun', action='store_true', default=False)
    p.add_argument('-x', dest='do_not_register',
                   action='store_true', default=False)
    p.add_argument('-i', '--insert-at', type=int, default=None)
    p.add_argument(axo, nargs='+', metavar=mx, help='Valid module name[s]')

    p = sub_p.add_parser(LOAD_FROM_FILE, parents=[pp], help='Load module[s] from file')
    p.add_argument('filename', help='Valid filename')

    p = sub_p.add_parser(PATH, parents=[pp], help='Show module path')

    p = sub_p.add_parser(PURGE, parents=[pp], help='Unload all modules')
    p.add_argument('--dryrun', action='store_true', default=False)
    p.add_argument('-F', action='store_true', default=False)

    p = sub_p.add_parser(REFRESH, parents=[pp],
                         help='Refresh (unload/reload) all modules')
    p.add_argument('--dryrun', action='store_true', default=False)

    p = sub_p.add_parser(RELOAD, parents=[pp], help='Reload module[s]')
    p.add_argument('--dryrun', action='store_true', default=False)
    p.add_argument(ax, nargs='+', metavar=mx, help='Valid module name[s]')

    p = sub_p.add_parser(SHOW, parents=[pp],
                         help='Display information about '
                              'modulefile[s] or collection')
    p.add_argument(axo, nargs='+', metavar=mx, help='Valid module name[s]')

    p = sub_p.add_parser(SWAP, parents=[pp], help='Swap modules')
    p.add_argument('--dryrun', action='store_true', default=False)
    p.add_argument(ax, nargs=2, metavar=mx, help='Valid module names')

    p = sub_p.add_parser(UNLOAD, parents=[pp], help='Unload module[s]')
    p.add_argument('--dryrun', action='store_true', default=False)
    p.add_argument(ax, nargs='+', metavar=mx, help='Valid module name[s]')

    p = sub_p.add_parser(POP, parents=[pp],
                         help='Unload module[s], but do not unload internally '
                              'loaded modules')
    p.add_argument('--dryrun', action='store_true', default=False)
    p.add_argument(ax, nargs='+', metavar=mx, help='Valid module name[s]')

    p = sub_p.add_parser(USE, parents=[pp], help='Add directory[s] to MODULEPATH')
    p.add_argument('--dryrun', action='store_true', default=False)
    p.add_argument(ax, nargs='+', metavar='dirname', help='Valid directory[s]')
    p.add_argument('-D', action='store_true', help='Unuse directory[s]')

    p = sub_p.add_parser(UNUSE, parents=[pp],
                         help='Remove directory[s] from MODULEPATH')
    p.add_argument('--dryrun', action='store_true', default=False)
    p.add_argument(ax, nargs='+', metavar='dirname', help='Valid directory[s]')

    p = sub_p.add_parser(WHATIS, parents=[pp],
                         help='Display module whatis string')
    p.add_argument(ax, nargs='+', metavar=mx, help='Valid module names')

    p = sub_p.add_parser(TEST, parents=[pp],
                         help='Run the modulecmd tests (requires pytest module)')
    p.add_argument('--coverage', action='store_true',
                   help='Environment variable to set')

    p = sub_p.add_parser(WHICH, parents=[pp], help='Show path to module file')
    p.add_argument(ax, nargs='+', metavar=mx, help='Valid module name')

    p = sub_p.add_parser(CAT, parents=[pp],
                         help='Concatenate contents to console')
    p.add_argument('name', help='Name of module, collection, or config file')

    p = sub_p.add_parser(MORE, parents=[pp], help='Page contents to console')
    p.add_argument('name', help='Name of module, collection, or config file')

    p = sub_p.add_parser('cache', parents=[pp], help='Cache modules')

    # --- Collections
    p2 = sub_p.add_parser(COLLECTION, parents=[pp])
    sub_p2 = p2.add_subparsers(dest='subcommand', title='subcommands')

    p = sub_p2.add_parser(AVAIL, parents=[pp],
                          help='Display list of available collections')
    p.add_argument('--dryrun', action='store_true', default=False)
    p.add_argument('-t', '--terse', default=False, action='store_true',
                   help='Display output in terse format [default: %(default)s]')

    p = sub_p2.add_parser(EDIT, parents=[pp], help='Edit a module collection')
    p.add_argument('name', help='The name of the collection to edit')

    p = sub_p2.add_parser(RESTORE, parents=[pp],
                          help='Restore (load) a module collection')
    p.add_argument('--dryrun', action='store_true', default=False)
    p.add_argument('-I', action='store_true', default=False,
                   help='Skip modules not found')
    p.add_argument('name', nargs='?',
                   help='The name of the collection to restore')

    p = sub_p2.add_parser(RM, parents=[pp], help='Remove module collection')
    p.add_argument('--dryrun', action='store_true', default=False)
    p.add_argument('name', help='Name of module collection to remove')

    p = sub_p2.add_parser(SAVE, parents=[pp],
                          help='Save currently loaded modules to a collection')
    p.add_argument('--dryrun', action='store_true', default=False)
    p.add_argument('-f', default=None)
    p.add_argument('name', nargs='?',
                   help='The name of the collection.  If not given, defaults '
                        'to user\'s default collection')

    p = sub_p2.add_parser(SHOW, parents=[pp],
                          help='Show commands to be executed by module restore')
    p.add_argument('--dryrun', action='store_true', default=False)
    p.add_argument('name', help='Collection to describe')

    # --- Clones
    p2 = sub_p.add_parser(CLONE, parents=[pp])
    sub_p2 = p2.add_subparsers(dest='subcommand', title='subcommands')

    p = sub_p2.add_parser(AVAIL, parents=[pp],
                          help='Display list of available clones')
    p.add_argument('--dryrun', action='store_true', default=False)
    p.add_argument('-t', '--terse', default=False, action='store_true',
                   help='Display output in terse format [default: %(default)s]')

    p = sub_p2.add_parser(RESTORE, parents=[pp],
                          help='Restore (load) an environemnt clone')
    p.add_argument('--dryrun', action='store_true', default=False)
    p.add_argument('name', help='The name of the clone to restore')

    p = sub_p2.add_parser(RM, parents=[pp], help='Remove environemnt clone')
    p.add_argument('--dryrun', action='store_true', default=False)
    p.add_argument('name', help='Name of module collection to remove')

    p = sub_p2.add_parser(SAVE, parents=[pp], help='Clone current environment')
    p.add_argument('--dryrun', action='store_true', default=False)
    p.add_argument('name', help='The name of the clone')

    p = sub_p2.add_parser(SHOW, parents=[pp],
                          help='Show commands to be executed')
    p.add_argument('--dryrun', action='store_true', default=False)
    p.add_argument('name', help='Clone to describe')

    # Environment modification
    p2 = sub_p.add_parser(SHELL, parents=[pp])
    sub_p2 = p2.add_subparsers(dest='subcommand', title='subcommands')

    p = sub_p2.add_parser(ALIAS, parents=[pp], help='List or set a shell alias')
    p.add_argument('arg', nargs='?',
                   help='If given, name of shell alias to list or shell aliases '
                        'to set, specified as name=value.  If not supplied, '
                        'list all shell aliases')
    p.add_argument('-D', action='store_true', help='Delete shell alias')

    p = sub_p2.add_parser(ENV, parents=[pp],
                          help='List or set environment variables')
    p.add_argument('envar', nargs='?',
                   help='Name of environment variable to list or '
                        'environment variable to set, specified as name=value.')
    p.add_argument('-D', action='store_true', help='Unset environment variable')

    # Send stdout to stderr so the shell does not interpret any output (usually
    # error messages) from parse_args.
    sys.stdout = sys.stderr
    args = p1.parse_args(argv)
    sys.stdout = sys.__stdout__

    if args.subparser is None:
        args.subparser = HELP
        args.argv = None

    if args.subparser == HELP and not args.argv:
        pager(help_page)
        if hasattr(sys, '_pytest_in_progress_'):
            raise Exception('Help fired')
        p1.exit()

    if args.time:  # pragma: no cover
        initial_time = time.time()
        atexit.register(total_module_time, initial_time)

    if args.subparser == TEST:  # pragma: no cover
        # Run the tests using pytest
        from subprocess import Popen
        try:
            import pytest
        except ImportError:
            raise SystemExit('pytest must be installed to run tests')
        # py.test writes help to stdout. But, we need it to be stderr since
        # this file should be `eval`d by the shell.

        tests_dir = os.path.join(PYMOD_DIR, 'test/')
        assert os.path.isdir(tests_dir)
        cov_cfg_file = os.path.join(tests_dir, '.coveragerc')
        assert os.path.isfile(cov_cfg_file)
        command = ['py.test']
        if args.coverage:
            command.extend(['--cov={0}'.format(PYMOD_PKG_DIR), #os.path.dirname(PYMOD_PKG_DIR)),
                            '--cov-report=html',
                            '--cov-config={0}'.format(cov_cfg_file)])
        command.append(tests_dir)
        p = Popen(command, stdout=sys.stderr, stderr=sys.stderr)
        p.wait()
        return p.returncode

    dryrun = getattr(args, 'dryrun', False)
    if args.verbosity is not None:
        cfg.verbosity = args.verbosity
    if args.debug:
        cfg.debug = args.debug
    mc = MasterController(shell=args.shell, dryrun=dryrun)

    if args.subparser == AVAIL:
        mc.show_available_modules(terse=args.terse, regex=args.regex,
                                  fulloutput=args.F)
        return 0

    elif args.subparser == INIT:
        mc.post_init(modulepath=args.mp)
        mc.dump(stream=sys.stdout)

    elif args.subparser == PATH:
        mc.show_modulepath()

    elif args.subparser == PURGE:
        mc.purge(allow_load_after_purge=not args.F)
        mc.dump(stream=sys.stdout)
        return 0

    elif args.subparser == COLLECTION:

        if args.subcommand is None:
            mc.show_available_collections(terse=args.terse)
            return 0

        elif args.subcommand == EDIT:
            mc.edit_collection(args.name)
            return 0

        elif args.subcommand == AVAIL:
            mc.show_available_collections(terse=args.terse)

        elif args.subcommand == RESTORE:
            cfg.stop_on_error = not bool(args.I)
            warn_if_missing = True
            if args.name is None:
                # Restore default collection
                args.name = defaults.DEFAULT_USER_COLLECTION_NAME
                warn_if_missing = False
            mc.restore(args.name, warn_if_missing=warn_if_missing)
            mc.dump(stream=sys.stdout)

        elif args.subcommand == RM:
            if args.name is None:
                sys.exit('collection to remove not specified')
            mc.remove_collection(args.name)
            return 0

        elif args.subcommand == SAVE:
            if args.f is not None:
                name = args.f
                if args.name is not None:
                    sys.exit('Do not specify both -f F and NAME')
            elif args.name is None:
                name = defaults.DEFAULT_USER_COLLECTION_NAME
            else:
                name = args.name
            mc.save_collection(name, isolate=args.f is not None)
            return 0

        elif args.subcommand == SHOW:
            mc.show_collection(args.name)
            return 0

        else:
            p1.print_help(file=sys.stderr)
            s = 'module: error: collection subcommand: invalid choice: {0!r}'
            sys.stderr.write(s.format(args.subcommand))

    elif args.subparser == CLONE:

        if args.subcommand in (AVAIL, None):
            terse = False if args.subcommand is None else args.terse
            mc.display_clones(terse=terse)

        elif args.subcommand == RESTORE:
            mc.restore_clone(args.name)
            mc.dump(stream=sys.stdout)
            return 0

        elif args.subcommand == RM:
            mc.remove_clone(args.name)
            return 0

        elif args.subcommand == SAVE:
            mc.clone_current_environment(args.name)
            return 0

        elif args.subcommand == SHOW:
            mc.restore_clone(args.name)
            mc.dump(stream=sys.stderr)
            return 0

        else:
            p1.print_help(file=sys.stderr)
            s = 'module: error: clone subcommand: invalid choice: {0!r}\n'
            sys.stderr.write(s.format(args.subcommand))

    elif args.subparser == SHELL:

        if args.subcommand is None:
            s  = 'usage: module [--profile] [--time] {0} <{1}> [<args>]\n'
            s += 'module: error: shell: missing required {1}\n'
            sys.stderr.write(s.format(SHELL, 'subcommand'))
            sys.exit(1)

        elif args.subcommand == ALIAS:
            arg = args.arg
            delete = args.D
            if arg is None:
                mc.list_aliases()
                return 0
            try:
                name, value = split(arg, '=')
            except ValueError:
                name, value = arg, None
            if not delete and value is None:
                mc.list_aliases(name)
                return
            if delete: aliases = {name: None}
            else: aliases = {name: value}
            s = mc.shell.dump([], {}, alias_keys=[name], aliases=aliases)
            if mc.dryrun:
                tty.info(s)
                return 0
            sys.stdout.write(s)

        elif args.subcommand == ENV:
            arg = args.envar
            delete = args.D
            if arg is None:
                mc.list_envar()
                return 0
            try:
                name, value = split(arg, '=')
            except ValueError:
                name, value = arg, None
            if delete:
                mc.set_envar(name, None)
            elif value is None:
                mc.list_envar(name)
            else:
                mc.set_envar(name, value)
            return 0

    if hasattr(args, ax):
        argv = args.argv or []

    elif hasattr(args, axo):
        # To pass arguments to a module, do
        #
        #  module <subcommand> module +option[=value]...
        #
        argv = []
        args.argvo = args.argvo or []
        for item in args.argvo:
            if item.startswith(MODULE_OPTION_PREFIX):
                if not argv:
                    msg = 'Options must be specified after module name'
                    tty.die(msg)
                if not ModuleOptionParser.is_valid_option_string(item):
                    msg = 'Invalid option {0!r} for module {1!r}'
                    tty.die(msg.format(item, argv[-1]))
                argv[-1][-1].append(item)
            else:
                argv.append((item, []))


    if args.subparser == SHOW:
        # Execute the module
        not_found = []
        for (name, opts) in argv:
            stat = mc.show(name, options=opts)
            if stat != 0:
                not_found.append(name)
        InstructionLogger.show()
        if not not_found:
            return
        s = 'Failed to find the following module(s) on MODULEPATH: '
        tty.info('\n' + colorize(s, 'magenta'))
        for (i, x) in enumerate(not_found):
            tty.info('  {0}) {1}'.format(i+1, x))

    elif args.subparser == CAT:
        pager(get_entity_text(mc, args.name), plain=True)
        return 0

    elif args.subparser == MORE:
        pager(get_entity_text(mc, args.name))
        return 0

    elif args.subparser in (FILE, WHICH):
        for modulename in argv:
            module = mc.get_module(modulename, raise_ex=1)
            write_to_console(module.filename)
        return 0

    elif args.subparser == EDIT:  # pragma: no cover
        for modulename in argv:
            mc.edit(modulename)
        return 0

    elif args.subparser == LIST:
        mc.show_loaded_modules(terse=args.terse, regex=args.regex,
                               show_command=args.show_command)
        return 0

    elif args.subparser == WHATIS:
        for modulename in argv:
            mc.display_info(modulename)
        return 0

    elif args.subparser == HELP:
        for modulename in argv:
            mc.display_help(modulename)
        return 0

    elif args.subparser == LOAD_FROM_FILE:
        for line in open(args.filename):
            line = line.strip()
            if line == 'Currently Loaded Modulefiles:':
                continue
            mc.load(line)
        mc.dump(stream=sys.stdout)
        return 0

    elif args.subparser == LOAD:
        for (name, opts) in argv:
            mc.load(name, options=opts, do_not_register=args.do_not_register,
                    insert_at=args.insert_at)
        mc.dump(stream=sys.stdout)
        return 0

    elif args.subparser == RELOAD:
        for modulename in argv:
            mc.reload(modulename)
        mc.dump(stream=sys.stdout)
        return 0

    elif args.subparser == UNLOAD:
        for name in argv:
            mc.unload(name)
        mc.dump(stream=sys.stdout)
        return 0

    elif args.subparser == POP:
        for name in argv:
            mc.pop(name)
        mc.dump(stream=sys.stdout)
        return 0

    elif args.subparser == REFRESH:
        mc.refresh()
        mc.dump(stream=sys.stdout)
        return 0

    elif args.subparser == SWAP:
        module_a, module_b = argv
        mc.swap(module_a, module_b)
        mc.dump(stream=sys.stdout)
        return 0

    elif args.subparser == USE:
        fun = mc.unuse if args.D else mc.use
        for dirname in argv:
            fun(dirname)
        mc.dump(stream=sys.stdout)
        return 0

    elif args.subparser == UNUSE:
        for dirname in argv:
            mc.unuse(dirname)
        mc.dump(stream=sys.stdout)
        return 0

    elif args.subparser == 'cache':
        mc.cache_modules_on_modulepath()


def get_entity_text(mc, name):
    module = mc.get_module(name)
    if module is not None:
        return open(module.filename).read()
    elif name in mc.collections:
        collection = mc.collections.get(name)
        return json.dumps(collection, default=serialize, indent=2)
    elif os.path.isfile(os.path.join(cfg.dot_dir, name + '.json')):
        return open(os.path.join(cfg.dot_dir, name + '.json')).read()
    sys.exit('Unknown named entity {0!r}'.format(name))


if __name__ == '__main__':

    if 'cache-system-modules' in sys.argv:
        assert len(sys.argv) == 3
        assert sys.argv.index('cache-system-modules') == 2
        sys.argv[2] = SAVE
        sys.argv.append(DEFAULT_SYS_COLLECTION_NAME)

    if '--profile' in sys.argv:
        sys.argv.remove('--profile')
        try:
            import cProfile as profile
        except ImportError:
            import profile
        output_file = os.path.join(os.getcwd(), 'modulecmd.stats')
        profile.run('main()', output_file)
    else:
        sys.exit(main())
