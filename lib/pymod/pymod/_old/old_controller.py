from __future__ import division, print_function
import os
import re
import json
import socket
from copy import deepcopy as copy
from collections import OrderedDict


from .constants import *
from .utils import *
from . import user
from .defaults import *
from .color import colorize
from .tty import tty, printc
from .trace import trace, trace_function
from .module2 import create_module_from_file, create_module_from_kwds, Module2
from .optparse import ModuleOptionParser
from .instruction_logger import InstructionLogger
from .pager import pager
from .trace import trace
from .shell import get_shell
from .config import cfg
from .environ import Environ
from .modulepath import Modulepath
from .collections2 import Collections


class InconsistentModuleState(Exception):
    def __init__(self, module):
        m = 'An inconsistent state occurred when trying to load module ' \
            '{0!r} that resulted in it not being found on MODULEPATH. '  \
            'This is probably due to a module modifying MODULEPATH and ' \
            'causing automatic changes in loaded/unloaded modules'
        msg = m.format(module.fullname)
        if cfg.verbosity < 2:
            tty.die(msg)
        else:
            super(InconsistentModuleState, self).__init__(msg)


class FamilyLoadedError(Exception):
    pass


class ModuleNotFoundError(Exception):
    def __init__(self, modulename, mp=None):
        msg = '{0!r} is not a module.  See {1!r}.'.format(
            modulename, 'module avail')
        if mp:
            candidates = mp.candidates(modulename)
            if candidates:
                msg += '\n\nDid you mean one of these?'
                msg += '\n\t{0}'.format('\t'.join(candidates))
        super(ModuleNotFoundError, self).__init__(msg)
        if cfg.verbosity < 2:
            tty.die(msg)
        else:
            super(ModuleNotFoundError, self).__init__(msg)


def assert_known_mode(mode):
    """Valid modes for loading/unloading modules"""
    assert mode in (LOAD, UNLOAD, NULLOP, WHATIS, HELP, SWAP, SHOW, LOAD_PARTIAL)


# --------------------------------------------------------------------------- #
# ----------------------- THE MASTER ENVIRONMENT ---------------------------- #
# --------------------------------------------------------------------------- #
class MasterController(object):
    def __init__(self, shell='bash', env=None, verbosity=None, dryrun=False):

        if env is None:
            env = os.environ

        if verbosity is not None:
            cfg.verbosity = int(verbosity)

        self.moduleopts = {}

        self.dryrun = dryrun
        self.shell = get_shell(shell)
        self.environ = Environ(env)
        self.load_for_show = False
        self.aliases = OrderedDict()
        self.shell_functions = OrderedDict()

        mp, extra = get_unique(split(self.environ[MP_KEY], os.pathsep))
        if extra:
            tty.warning('Removing duplicate paths in MODULEPATH: '
                            '{0!r}'.format(','.join(extra)),
                            minverbosity=2)
        lm_files = self.environ.get_loaded_modules('filenames')
        self.modulepath = Modulepath(mp)
        self.modulepath.apply(self.mark_loaded_module)
        self.collections = Collections()

        self.m_state_changed = {}

        self.moduleshome = os.getenv('PYMOD_DIR', PYMOD_DIR)

    def __getitem__(self, key):
        return self.environ[key]

    def __contains__(self, key):
        return key in self.environ

    @trace
    def create_module_from_filename(self, filename):
        """Create the module from explicit filename"""
        assert os.path.isfile(filename), '{0} does not exist'.format(filename)
        modulepath = os.path.dirname(filename)
        module = create_module_from_file(modulepath, filename, False)
        self.modulepath.append(module.modulepath)
        self.environ[MP_KEY] = self.modulepath.join()
        return module

    @trace
    def get(self, key, default=None):
        return self.environ.get(key, default)


    @trace
    def set_moduleopts(self, module, m_opts):
        self.moduleopts[module.fullname] = m_opts
        self.moduleopts[module.name] = m_opts

    @trace
    def get_moduleopts(self, module):
        if module.fullname in self.moduleopts:
            return self.moduleopts[module.fullname]
        elif module.name in self.moduleopts:
            return self.moduleopts[module.name]
        return None

    @trace
    def get_loaded_modules(self, key=None, reverse=False,
                           names_and_short_names=False):
        loaded_modules = []
        lm_files = self.environ.get_loaded_modules('filenames')
        for (i, filename) in enumerate(lm_files):
            module = self.modulepath.get_module_by_filename(filename)
            if module is None:
                lm_names = self.environ.get_loaded_modules('names')
                raise Exception('Loaded module {0!r} is not '
                                'available!'.format(lm_names[i]))
            loaded_modules.append(module)

        if key is not None:
            loaded_modules = [m for m in loaded_modules if key(m)]

        if names_and_short_names:
            lm = {}
            for m in loaded_modules:
                if m in lm and not m.is_default:
                    continue
                lm[m.fullname] = m
                lm[m.name] = m
            loaded_modules = lm

        if reverse:
            assert not names_and_short_names
            loaded_modules = [m for m in reversed(loaded_modules)]

        return loaded_modules

    @trace
    def reload(self, modulename):
        """Reload the module given by `modulename`"""
        module = self.modulepath.get_module_by_name(modulename)
        if module is None:
            raise ModuleNotFoundError(modulename, self.modulepath)
        if not module.is_loaded:
            tty.warning('{0} is not loaded!'.format(module.fullname))
            return
        options = self.environ.get_loaded_modules('opts', module=module)
        assert module.is_loaded
        self.swap2(module, module, options_b=options, maintain_state=1)
        return

    @trace
    def pop(self, modulename):
        loaded = self.get_loaded_modules(names_and_short_names=True)
        module = loaded.get(modulename)
        if module is None:
            return None
        self.remove_module(module)
        return None

    @trace
    def unload(self, modulename, tolerant=False):
        """Unload the module given by `modulename`"""
        loaded = self.get_loaded_modules(names_and_short_names=True)
        module = loaded.get(modulename)
        if module is not None:
            mode = UNLOAD
            self.execmodule(mode, module)
            return None

        # Module is not loaded!
        msg = 'Requesting to unload {0}, but {0} is not loaded'.format(modulename)
        if self.modulepath.get_module_by_name(modulename) is None:
            # and modulename is not a module!
            msg += ' (nor is it a module)'
        tty.warning(msg)
        return None

    @trace
    def refresh(self):
        """Purge all modules from environment"""
        loaded = self.get_loaded_modules(reverse=True)
        for module in loaded:
            self.execmodule(UNLOAD, module)
        for module in loaded[::-1]:
            self.execmodule(LOAD, module)
        now_loaded = self.get_loaded_modules(reverse=True)
        assert lists_are_same(loaded, now_loaded, key=lambda x: x.filename)

    @trace

    @trace
    def show(self, modulename, options=None, stream=sys.stderr):

        if modulename.lower() == 'modulepath':
            _, width = get_console_dims()
            string = '{0}'.format(' MODULEPATH '.center(width, '=')) + '\n'
            string += wrap2(self.modulepath.path, width, numbered=True)
            stream.write(string+'\n')
            return 0

        warn_all_cache = cfg.warn_all
        cfg.warn_all = False

        module = self.get_module(modulename)
        if module is None:
            if modulename in self.collections:
                return self.show_collection(modulename)
            return 1

        self.load_for_show = True
        if options:
            self.set_moduleopts(module, options)

        self.execmodule(LOAD, module)

        # Restore old values
        cfg.warn_all = warn_all_cache

        return 0

    @trace
    def show_modulepath(self, stream=sys.stderr):
        s = self.modulepath.describe(pathonly=True)
        stream.write(s)
        return None

    @trace
    def show_available_modules(self, terse=False, regex=None, fulloutput=False,
                               stream=sys.stderr):
        s = self.modulepath.describe(terse=terse, regex=regex,
                                     fulloutput=fulloutput)
        stream.write(s)
        stream.write("\n")
        s = self.collections.describe(terse=terse, regex=regex)
        stream.write(s)
        return None

    @trace
    def set_envar(self, key, value, stream=sys.stdout):
        """Set environment variables manually."""
        kwds = {}
        kwds[key] = value
        s = self.shell.dump(kwds.keys(), kwds)
        if self.dryrun:
            tty.info(s)
            return 0
        stream.write(s)

    @trace
    def list_envar(self, envar=None, stream=sys.stderr):
        """List environment variable"""
        for (key, val) in self.environ.items():
            if envar is None:
                stream.write('module shell env {0}={1}\n'.format(key, val))
            elif key.upper() == envar.upper():
                stream.write('module shell env {0}={1}\n'.format(key, val))
                break

    @trace
    def list_aliases(self, alias=None, stream=sys.stdout):
        """List environment variable"""
        if alias is None:
            stream.write(ALIAS)
        else:
            stream.write('alias {0}'.format(alias))

    @trace
    def remove_envar(self, envar):
        """List environment variable"""
        self.set_envar(envar, None)

    @trace
    def display_info(self, modulename, stream=sys.stderr):
        """Display 'whatis' message for the module given by `modulename`"""
        module = self.get_module(modulename)
        if module is None:
            raise ModuleNotFoundError(modulename, self.modulepath)
        self.load_for_show = True
        self.execmodule(LOAD, module)
        height, width = get_console_dims()
        x = " " + module.name + " "
        s = '{0}'.format(x.center(width, '=')) + '\n'
        s += module.whatis + '\n'
        s += '=' * width
        stream.write(s + '\n')

    @trace
    def display_help(self, modulename, stream=sys.stderr):
        """Display 'help' message for the module given by `modulename`"""
        module = self.get_module(modulename)
        if module is None:
            raise ModuleNotFoundError(modulename, self.modulepath)
        self.execmodule(LOAD, module)
        height, width = get_console_dims()
        x = " " + module.name + " "
        s = '{0}'.format(x.center(width, '=')) + '\n'
        s += module.helpstr + '\n'
        s += '=' * width
        stream.write(s + '\n')

    @trace
    def edit(self, modulename):
        """Load the module given by `modulename`"""

        module = self.get_module(modulename)
        if module is None:
            raise ModuleNotFoundError(modulename, self.modulepath)

        filename = module.filename
        if cfg.tests_in_progress:
            sys.stdout.write('vim {0}'.format(filename))
            return
        edit_file(filename)

    # -------------------------- SANDBOX FUNCTIONS -------------------------- #
    @trace
    def execmodule(self, mode, module, do_not_register=False):
        """Execute the module in a sandbox"""
        assert_known_mode(mode)
        try:
            out = self.execmodule_in_sandbox(mode, module,
                                             do_not_register=do_not_register)

            lm_refcnt = str2dict(self.environ.get(LM_REFCNT_KEY()))
            if mode == LOAD:
                lm_refcnt[module.fullname] = 1
            elif mode in (UNLOAD, ):
                lm_refcnt.pop(module.fullname, None)
            self.environ[LM_REFCNT_KEY()] = dict2str(lm_refcnt)

            return out

        except FamilyLoadedError as e:
            # Module of same family already loaded, unload it first

            # This comes after first trying to load the module because the
            # family is set within the module, so the module must first be
            # loaded to determine the family. If when the family is being set
            # it is discovered that a module from the same family is loaded,
            # the FamilyLoadedError is raised.

            # This should only happen in load mode
            assert mode == LOAD
            other = self.modulepath.get_module_by_name(e.args[0])
            args = [other.family, other.fullname, module.fullname]
            self.m_state_changed.setdefault('FamilyChange', []).append(args)
            assert other.is_loaded
            self.swap2(other, module)

    @trace
    def execmodule_in_sandbox(self, mode, module, do_not_register=False):
        """Execute filename in sandbox"""

        if module.type not in (M_PY, M_TCL):
            tty.die('Module {0!r} has unknown module type: '
                          '{1!r}'.format(module.fullname, module.type))

        if mode in (UNLOAD,):
            opts = self.environ.get_loaded_modules('opts', module=module)
        else:
            opts = self.get_moduleopts(module)
        InstructionLogger.start_new_instructions(
            module.fullname, module.filename)

        try:
            self._execmodule(mode, module, opts)
        except FamilyLoadedError as e:
            raise e
        else:
            if mode == LOAD:
                self.on_module_load(module, do_not_register=do_not_register)
            elif mode in (UNLOAD,):
                self.on_module_unload(module)

        return None

    # ----------------------------- MODULE EXECUTION FUNCTIONS
    def _execmodule(self, mode, module, moduleopts):
        """Execute python module in sandbox"""

        module.reset_state()
        ns = {
            'os': os,
            're': re,
            'sys': sys,
            'my': user.user_env,
            'user_env': user.user_env,
            'HOME': os.getenv('HOME'),
            'USER': os.getenv('USER'),
            'getenv': self.environ.get,
            'env': self.environ.copy(),
            'listdir': listdir,
            'system_is_darwin': lambda: IS_DARWIN,
            'IS_DARWIN': IS_DARWIN,
            'get_hostname': socket.gethostname,
            'mode': lambda: mode,
            'self': module,
            'colorize': colorize,
            #
            'add_option': lambda x, **k: module.add_option(x, **k),
            'add_mutually_exclusive_option': \
            lambda x, y, **k: module.add_mutually_exclusive_option(x, y, **k),
            'parse_opts': lambda: module.parse_opts(moduleopts),
            #
            'log_message': self.wrap_mf_tty_info(mode, module.filename),
            'log_info': self.wrap_mf_tty_info(mode, module.filename),
            'log_warning': self.wrap_mf_tty_warning(mode, module.filename),
            'log_error': self.wrap_mf_tty_error(mode, module.filename),
            'execute': self.wrap_mf_execute(mode),
            #
            'setenv': self.wrap_mf_setenv(mode),
            'unsetenv': self.wrap_mf_unsetenv(mode),
            #
            USE: self.wrap_mf_use(mode),
            UNUSE: self.wrap_mf_unuse(mode),
            #
            'set_alias': self.wrap_mf_set_alias(mode),
            'unset_alias': self.wrap_mf_unset_alias(mode),
            #
            'set_shell_function': self.wrap_mf_set_shell_function(mode),
            'unset_shell_function': self.wrap_mf_unset_shell_function(mode),
            #
            'prereq': self.wrap_mf_prereq(mode),
            'prereq_any': self.wrap_mf_prereq_any(mode),
            'conflict': self.wrap_mf_conflict(mode, module.name),
            #
            LOAD: self.wrap_mf_load(mode),
            SWAP: self.wrap_mf_swap(mode),
            'load_first': self.wrap_mf_load_first(mode),
            UNLOAD: self.wrap_mf_unload(mode),
            'is_loaded': self.wrap_mf_is_loaded(mode),
            #
            'family': self.wrap_mf_family(mode, module),
            #
            'prepend_path': self.wrap_mf_prepend_path(mode),
            'append_path': self.wrap_mf_append_path(mode),
            'remove_path': self.wrap_mf_remove_path(mode),
            #
            WHATIS: self.wrap_mf_whatis(mode, module),
            HELP: self.wrap_mf_help(mode, module),
            'which': which,
            'check_output': check_output,
            #
            'source': self.wrap_mf_source(mode),
        }

        # Execute the environment
        s = module.data(mode, self.environ)
        code = compile(s, module.filename, 'exec')
        execfun(code, ns, {})
        #try:
        #    execfun(code, ns, {})
        #except Exception as e:
        #    msg = 'Failed to {0} {1} with the following error:\n{2}'.format(
        #        mode, module.fullname, e.args[0])
        #    tty.die(msg)

    @trace
    def cache_modules_on_modulepath(self):
        self.modulepath.cache(self.environ)

    # ------------------- FUNCTIONS PASSED TO MODULE FILES ------------------ #
    def wrap_mf_whatis(self, mode, module):
        def mf_whatis(*args, **kwargs):
            module.set_whatis(*args, **kwargs)
        return mf_whatis

    def wrap_mf_help(self, mode, module):
        def mf_help(helpstr):
            module.helpstr = helpstr
        return mf_help

    def wrap_mf_unload(self, mode):
        """Function to pass to modules to unload other modules"""
        def mf_unload(modulename):
            if mode == LOAD_PARTIAL:
                return
            self.cb_unload(mode, modulename)
        return mf_unload

    def wrap_mf_load(self, mode):
        """Function to pass to modules to load other modules"""
        def mf_load(modulename, options=None):
            if mode == LOAD_PARTIAL:
                return
            self.cb_load(mode, modulename, options=options)
        return mf_load

    def wrap_mf_swap(self, mode):
        """Function to pass to modules to load other modules"""
        def mf_swap(m1, m2):
            if mode == LOAD_PARTIAL:
                return
            self.cb_swap(mode, m1, m2)
        return mf_swap

    def wrap_mf_load_first(self, mode):
        """Function to pass to modules to load other modules"""
        def mf_load_first(*modulenames):
            if mode == LOAD_PARTIAL:
                return
            self.cb_load(mode, load_first_of=modulenames)
        return mf_load_first

    def wrap_mf_is_loaded(self, mode):
        """Function to pass to modules to load other modules"""
        def mf_is_loaded(modulename):
            return self.cb_is_loaded(modulename)
        return mf_is_loaded

    def wrap_mf_source(self, mode):
        """Function to pass to modules to load other modules"""
        def mf_source(filename):
            return self.cb_source(mode, filename)
        return mf_source

    def wrap_mf_setenv(self, mode):
        """Set value of environment variable `name`"""
        def mf_setenv(name, value, **kwds):
            if mode in (LOAD,):
                self.setenv(name, value, **kwds)
            elif mode in (UNLOAD,):
                self.unsetenv(name, **kwds)
            else:
                # in all other modes, setenv is a null op
                pass
        return mf_setenv

    def wrap_mf_unsetenv(self, mode):
        """Set value of environment variable `name`"""
        def mf_unsetenv(name, *args, **kwargs):
            if mode in (LOAD,):
                self.unsetenv(name)
            else:
                # in all other modes, setenv is a null op
                pass
        return mf_unsetenv

    def wrap_mf_use(self, mode):
        def mf_use(value, append=False):
            if mode in (LOAD,):
                self.cb_use(value, append=append)
            elif mode in (UNLOAD,):
                self.cb_unuse(value)
            else:
                # in all other modes, setenv is a null op
                pass
        return mf_use

    def wrap_mf_unuse(self, mode):
        """Set value of environment variable `name`"""
        def mf_unuse(value):
            if mode in (LOAD,):
                self.cb_unuse(value)
            else:
                # in all other modes, setenv is a null op
                pass
        return mf_unuse

    def wrap_mf_set_alias(self, mode):
        """Set value of environment variable `name`"""
        def mf_set_alias(name, value):
            if mode in (LOAD, LOAD_PARTIAL):
                self.set_alias(name, value)
            elif mode in (UNLOAD,):
                self.unset_alias(name)
            else:
                # in all other modes, setenv is a null op
                pass
        return mf_set_alias

    def wrap_mf_unset_alias(self, mode):
        """Set value of environment variable `name`"""
        def mf_unset_alias(name):
            if mode in (LOAD, LOAD_PARTIAL):
                self.unset_alias(name)
            else:
                # in all other modes, setenv is a null op
                pass
        return mf_unset_alias

    def wrap_mf_set_shell_function(self, mode):
        """Set value of environment variable `name`"""
        def mf_set_shell_function(name, value):
            if mode in (LOAD, LOAD_PARTIAL):
                self.set_shell_function(name, value)
            elif mode in (UNLOAD,):
                self.unset_shell_function(name)
            else:
                # in all other modes, setenv is a null op
                pass
        return mf_set_shell_function

    def wrap_mf_unset_shell_function(self, mode):
        """Set value of environment variable `name`"""
        def mf_unset_shell_function(name):
            if mode in (LOAD, LOAD_PARTIAL):
                self.unset_shell_function(name)
            else:
                # in all other modes, setenv is a null op
                pass
        return mf_unset_shell_function

    def wrap_mf_prereq_any(self, mode):
        def mf_prereq_any(*modulenames):
            if mode in (LOAD,):
                self.prereq_any(*modulenames)
            else:
                # in all other modes, setenv is a null op
                pass
        return mf_prereq_any

    def wrap_mf_prereq(self, mode):
        def mf_prereq(*modulenames):
            if mode in (LOAD,):
                self.prereq(*modulenames)
            else:
                # in all other modes, setenv is a null op
                pass
        return mf_prereq

    def wrap_mf_conflict(self, mode, name):
        def mf_conflict(*modulenames):
            if mode in (LOAD,):
                self.conflict(name, *modulenames)
            else:
                # in all other modes, setenv is a null op
                pass
        return mf_conflict

    def wrap_mf_append_path(self, mode):
        """Append `value` to path-like variable `name`"""
        def mf_append_path(name, *values, **kwds):
            if mode in (LOAD,):
                self.append_path(name, *values, **kwds)
            elif mode in (UNLOAD,):
                self.remove_path(name, *values, **kwds)
            else:
                # in all other modes, setenv is a null op
                pass
        return mf_append_path

    def wrap_mf_prepend_path(self, mode):
        """Prepend `value` to path-like variable `name`"""
        def mf_prepend_path(name, *values, **kwds):
            if mode in (LOAD,):
                self.prepend_path(name, *values, **kwds)
            elif mode in (UNLOAD,):
                self.remove_path(name, *values, **kwds)
            else:
                # in all other modes, setenv is a null op
                pass
        return mf_prepend_path

    def wrap_mf_remove_path(self, mode):
        """Append `value` to path-like variable `name`"""
        def mf_remove_path(name, *values, **kwds):
            if mode in (LOAD,):
                self.remove_path(name, *values, **kwds)
            else:
                # in all other modes, setenv is a null op
                pass
        return mf_remove_path

    def wrap_mf_family(self, mode, module):
        """Assign a family"""
        def mf_family(family_name):
            self.family(mode, family_name, module)
        return mf_family

    def wrap_mf_execute(self, mode_):
        import subprocess

        def mf_execute(command, mode=None):
            if mode is not None and mode != mode_:
                return
            with open(os.devnull, 'a') as fh:
                the_env = dict([item for item in self.environ.items()
                                if item[1] is not None])
                xc = split(command, ' ')
                try:
                    p = subprocess.Popen(xc, env=the_env, stdout=fh,
                                         stderr=subprocess.sys.stdout)
                    p.wait()
                except:
                    tty.warning('Command {0!r} failed'.format(command))
            return
        return mf_execute

    def wrap_mf_tty_info(self, mode, filename):
        @trace(name='log_message')
        def mf_tty_info(message):
            tty.info(message, filename)
        return mf_tty_info

    def wrap_mf_tty_warning(self, mode, filename):
        @trace(name='log_warning')
        def mf_tty_warning(message):
            tty.warning(message, filename)
        return mf_tty_warning

    def wrap_mf_tty_error(self, mode, filename):
        @trace(name='log_error')
        def mf_tty_error(message, noraise=0):
            noraise = noraise or self.load_for_show
            tty.die(message, filename, noraise=noraise)
        return mf_tty_error

    # ---------------- FUNCTIONS THAT MODIFY THE ENVIRONMENT ---------------- #
    @InstructionLogger.log_instruction
    def setenv(self, name, value, **kwds):
        """Set value of environment variable `name`"""
        if name == 'MODULEPATH':
            tty.die('MODULEPATH cannot be set by setenv')
        if IS_DARWIN and name == 'LD_LIBRARY_PATH':
            name = 'DYLD_LIBRARY_PATH'
        self.environ[name] = value
        if kwds.get('mkdir'):
            if not os.path.isdir(value):
                os.makedirs(value)
        return None

    @InstructionLogger.log_instruction
    def unsetenv(self, name, **kwds):
        """Unset value of environment variable `name`"""
        if kwds.get('persist'):
            return
        if name == 'MODULEPATH':
            tty.die('MODULEPATH cannot be unset by unsetenv')
        if IS_DARWIN and name == 'LD_LIBRARY_PATH':
            name = 'DYLD_LIBRARY_PATH'
        self.environ[name] = None
        return None

    @InstructionLogger.log_instruction
    def set_alias(self, name, value):
        """Set value of alias `name`"""
        self.aliases[name] = value
        return None

    @InstructionLogger.log_instruction
    def unset_alias(self, name):
        """Set value of alias `name`"""
        self.aliases[name] = None
        return None

    @InstructionLogger.log_instruction
    def set_shell_function(self, name, value):
        """Set value of alias `name`"""
        self.shell_functions[name] = value
        return None

    @InstructionLogger.log_instruction
    def unset_shell_function(self, name):
        """Set value of alias `name`"""
        self.shell_functions[name] = None
        return None

    @InstructionLogger.log_instruction
    def prereq_any(self, *modulenames):
        if self.load_for_show:
            return
        loaded = self.get_loaded_modules(names_and_short_names=True)
        for modulename in modulenames:
            if modulename in loaded:
                return
        tty.die('One of the prerequisites {0!r} must '
                      'first be loaded'.format(modulenames))

    @InstructionLogger.log_instruction
    def prereq(self, *modulenames):
        if self.load_for_show:
            return
        loaded = self.get_loaded_modules(names_and_short_names=True)
        for modulename in modulenames:
            if modulename in loaded:
                continue
            tty.die('Prerequisite {0!r} must '
                          'first be loaded'.format(modulename))

    @InstructionLogger.log_instruction
    def conflict(self, name, *modulenames):
        if self.load_for_show:
            return
        loaded = self.get_loaded_modules(names_and_short_names=True)
        for modulename in modulenames:
            if modulename in loaded:
                if cfg.resolve_conflicts:
                    # Unload the conflicting module
                    self.unload(modulename)
                else:
                    msg  = 'Module {name!r} conflicts with loaded module '
                    msg += '{modulename!r}. Set environment variable '
                    msg += 'PYMOD_RESOLVE_CONFLICTS=1 to let pymod resolve '
                    msg += 'conflicts.'
                    tty.die(msg.format(name=name, modulename=modulename))

    @trace
    def append_path(self, name, *values, **kwds):
        """Append `value` to path-like variable `name`"""
        if name == 'MODULEPATH':
            for value in values:
                self.use(value, append=True)
            return None
        self.modify_pathlike_variable(APPEND, name, *values, **kwds)

    @trace
    def prepend_path(self, name, *values, **kwds):
        """Prepend `value` to path-like variable `name`"""
        if name == 'MODULEPATH':
            for value in values[::-1]:
                self.use(value)
            return None
        self.modify_pathlike_variable(PREPEND, name, *values, **kwds)

    @trace
    def remove_path(self, name, *values, **kwds):
        """Append `value` to path-like variable `name`"""
        if kwds.get('persist'):
            return
        if name == 'MODULEPATH':
            for value in values:
                self.unuse(value)
            return None
        self.modify_pathlike_variable(REMOVE, name, *values, **kwds)

    @trace
    def modify_pathlike_variable(self, action, name, *values, **kwds):
        """Modify path-like variable `name`"""
        assert action in (APPEND, PREPEND, REMOVE)

        if kwds.get('persist') and action == REMOVE:
            return

        # Keep track of reference counting.  Each time a value is added to
        # a path, a reference count is incremented.  On unload, the value is
        # removed from path iff the reference count is 1.  That way, for
        # example, if two modules add `BAZ` to `SPAM`, `BAZ` will only be
        # removed when *both* modules are unloaded and not when the first is
        # unloaded.
        LM_REFCNT_NAME = LM_REFCNT_KEY(name)
        rc_d = str2dict(self.environ.get(LM_REFCNT_NAME))

        sep = kwds.pop('sep', os.pathsep)
        if IS_DARWIN and name == 'LD_LIBRARY_PATH':
            name = 'DYLD_LIBRARY_PATH'

        # Make sure each path in values is its own path
        values = [x for y in values for x in y.split(sep)]

        if action == PREPEND:
            values = reversed(values)

        curpath = split(self.environ.get(name), sep)
        if name.endswith('LD_LIBRARY_PATH'):
            # sometimes python doesn't pick up ld_library_path :(
            backup_curpath = split(self.environ.get('__ld_library_path__'), sep)
            if not curpath and backup_curpath:
                curpath = backup_curpath

        for path_val in values:
            refcount = None
            instruction = '{0}_path({1!r}, {2!r})'.format(action,
                                                          name, path_val)
            InstructionLogger.append(instruction)
            if action == REMOVE:
                if path_val not in curpath:
                    # check if realpath is
                    if os.path.realpath(path_val) in curpath:
                        path_val = os.path.realpath(path_val)
                    else:
                        continue
                refcount = rc_d.get(path_val, 1)
                if refcount == 1:
                    curpath.remove(path_val)
                refcount -= 1
            else:
                refcount = rc_d.get(path_val, 0)
                refcount += 1
                if path_val in curpath:
                    continue
                if action == APPEND:
                    curpath.append(path_val)
                elif action == PREPEND:
                    curpath.insert(0, path_val)

        if refcount == 0:
            rc_d.pop(path_val, None)
            self.environ[LM_REFCNT_NAME] = dict2str(rc_d)
        elif refcount is not None:
            rc_d[path_val] = refcount
            self.environ[LM_REFCNT_NAME] = dict2str(rc_d)
        self.environ[name] = join(curpath, sep)
        if name.endswith('LD_LIBRARY_PATH'):
            # sometimes python doesn't pick up ld_library_path :(
            self.setenv('__ld_library_path__', join(curpath, sep))
        if action == REMOVE and not self.environ[name]:
            self.environ[name] = None
