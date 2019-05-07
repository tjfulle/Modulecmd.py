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
    def pop(self, modulename):
        loaded = self.get_loaded_modules(names_and_short_names=True)
        module = loaded.get(modulename)
        if module is None:
            return None
        self.remove_module(module)
        return None

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
    def list_envar(self, envar=None, stream=sys.stderr):
        """List environment variable"""
        for (key, val) in self.environ.items():
            if envar is None:
                stream.write('module shell env {0}={1}\n'.format(key, val))
            elif key.upper() == envar.upper():
                stream.write('module shell env {0}={1}\n'.format(key, val))
                break

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
