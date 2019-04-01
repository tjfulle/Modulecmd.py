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
from .logging import logging, printc
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
            logging.error(msg)
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
            logging.error(msg)
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
            logging.warning('Removing duplicate paths in MODULEPATH: '
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

    def post_init(self, modulepath=None):
        for path in modulepath.split(os.pathsep):
            if not path.split():
                continue
            d = os.path.normpath(path)
            if os.path.isdir(d):
                self.use(d)
        self.restore_collection(DEFAULT_USER_COLLECTION_NAME)

    def mark_loaded_module(self, module):
        lm_files = self.environ.get_loaded_modules('filenames')
        module.is_loaded = module.filename in lm_files

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
    def get_module(self, name, raise_ex=0):
        if os.path.sep in name and os.path.isfile(name):
            module = self.modulepath.get_module_by_filename(name)
            if module is None:
                # requested a module not on MODULEPATH
                module = self.create_module_from_filename(name)
        else:
            module = self.modulepath.get_module_by_name(name)
        if raise_ex and module is None:
            raise ModuleNotFoundError(name, self.modulepath)
        return module

    @trace
    def get(self, key, default=None):
        return self.environ.get(key, default)

    @trace
    def add_module(self, module):
        assert not module.is_loaded, 'Module should not be loaded now'
        lm_names = self.environ.get_loaded_modules('names')
        lm_files = self.environ.get_loaded_modules('filenames')
        if module.fullname not in lm_names:
            lm_names.append(module.fullname)
            self.environ.set_loaded_modules('names', lm_names)
            if module.filename in lm_files:
                raise Exception('Path for {0} SHOULD NOT be in _LMFILES_ '
                                'at this point (1)!'.format(module))
            lm_files.append(module.filename)
            self.environ.set_loaded_modules('filenames', lm_files)
        elif module.filename not in lm_files:
            raise Exception('Path for {0} SHOULD be in _LMFILES_ '
                            'at this point (2)!'.format(module))
        lm_opts = self.environ.get_loaded_modules('opts')
        if module.fullname not in lm_opts:
            opts = module.get_set_options()
            lm_opts[module.fullname] = opts
            self.environ.set_loaded_modules('opts', lm_opts)
        module.is_loaded = True

    @trace
    def remove_module(self, module):
        assert module.is_loaded, 'Module should be loaded now'
        lm_names = self.environ.get_loaded_modules('names')
        lm_files = self.environ.get_loaded_modules('filenames')
        if module.fullname in lm_names:
            i = lm_names.index(module.fullname)
            lm_names.pop(i)
            self.environ.set_loaded_modules('names', lm_names)
            if lm_files[i] != module.filename:
                raise Exception('Path for {0} SHOULD be in _LMFILES_ '
                                'at this point (1)!'.format(module))
            lm_files.pop(i)
            self.environ.set_loaded_modules('filenames', lm_files)
        elif module.filename in lm_files:
            raise Exception('Path for {0} SHOULD NOT be in _LMFILES_ '
                            'at this point (2)!'.format(module))
        lm_opts = self.environ.get_loaded_modules('opts')
        if module.fullname in lm_opts:
            lm_opts.pop(module.fullname)
            self.environ.set_loaded_modules('opts', lm_opts)
        module.is_loaded = False

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
    def on_module_load(self, module, do_not_register=False):
        """Register the `module` to the list of loaded modules"""
        # Update the environment
        if module.modulepath not in self.modulepath:
            raise InconsistentModuleState(module)
        if cfg.skip_add_devpack and module.name.startswith('devpack'):
            return
        if do_not_register:
            return
        if module.do_not_register:
            return
        if not module.is_loaded:
            self.add_module(module)
        if module.fullname not in self.environ.get_loaded_modules('names'):
            msg = 'Expected to find {0} in LOADEDMODULES'.format(module)
            logging.error(msg)

    @trace
    def on_module_unload(self, module):
        """Unregister the `module` to the list of loaded modules"""
        # Update the environment
        # Make sure this module is removed
        if module.is_loaded:
            self.remove_module(module)
        loaded = self.environ.get_loaded_modules('names')
        if loaded and module.fullname in loaded:
            raise Exception('{0} module still in {1}!'.format(module, LM_KEY))

    # -------------------------- LOADER/UNLOADER ---------------------------- #
    @trace
    def report_changed_module_state(self):

        # Report swapped
        pairs = self.m_state_changed.get('Swapped')
        if pairs:
            logging.info('\nThe following modules have been swapped')
            for (i, (a, b)) in enumerate(pairs):
                logging.info('  {0}) {1} => {2}'.format(i+1, a, b))

        # Report reloaded
        pairs = self.m_state_changed.get('FamilyChange')
        if pairs:
            logging.info('\nThe following modules in the same family have '
                         'been updated with a version change:')
            for (i, (fam, a, b)) in enumerate(pairs):
                logging.info('  {0}) {1} => {2} ({3})'.format(i+1, a, b, fam))

        pairs = self.m_state_changed.get('VersionChanged')
        if pairs:
            logging.info('\nThe following modules have been updated '
                         'with a version change:')
            for (i, (a, b)) in enumerate(pairs):
                logging.info('  {0}) {1} => {2}'.format(i+1, a, b))

        # Report changes due to to change in modulepath
        on_mp_changed = self.m_state_changed.get('MP')
        if on_mp_changed:
            unloaded = [m for m in on_mp_changed.get('U', []) if not m.is_loaded]
            if unloaded:
                logging.info('\nThe following modules have been unloaded '
                             'with a MODULEPATH change:')
                for (i, m) in enumerate(unloaded):
                    logging.info('  {0}) {1}'.format(i+1, m.fullname))

            swapped = on_mp_changed.get('Up')
            if swapped:
                logging.info('\nThe following modules have been updated '
                             'with a MODULEPATH change:')
                for (i, (m1, m2)) in enumerate(swapped):
                    s1, s2 = m1.fullname, m2.fullname
                    logging.info('  {0}) {1} => {2}'.format(i+1, s1, s2))

    @trace
    def cb_swap(self, mode, m1, m2):
        assert_known_mode(mode)
        if mode == UNLOAD:
            # We don't swap modules in unload mode
            return
        s = '{0!r}, {1!r}'.format(m1, m2)
        InstructionLogger.append('swap({0})'.format(s))
        module_a = self.modulepath.get_module_by_name(m1)
        module_b = self.modulepath.get_module_by_name(m2)
        if module_a is None:
            raise ModuleNotFoundError(m1)
        if module_b is None:
            raise ModuleNotFoundError(m2)
        if module_b.is_loaded:
            return
        if not module_a.is_loaded:
            self.execmodule(LOAD, module_b)
            return
        assert module_a.is_loaded
        self.swap2(module_a, module_b)

    @trace
    def cb_load(self, mode, modulename=None, load_first_of=None, options=None):
        assert_known_mode(mode)
        if load_first_of is not None:
            s = UNLOAD if mode == UNLOAD else LOAD
            names = ','.join(x for x in load_first_of if x is not None)
            InstructionLogger.append('{0}({1!r})'.format(s, names))
            for modulename in load_first_of:
                if modulename is None:
                    continue
                if self.modulepath.get_module_by_name(modulename) is not None:
                    break
            else:
                if mode == UNLOAD:
                    return None
                elif modulename is None:
                    # Passes modulename = None as last argument says to ignore
                    # if this module is not found
                    return None
                raise ModuleNotFoundError(','.join(load_first_of))
        assert modulename is not None
        s = UNLOAD if mode == UNLOAD else LOAD
        InstructionLogger.append('{0}({1!r})'.format(s, modulename))
        if mode == UNLOAD:
            # We are in unload mode and the module was requested to be loaded.
            # So, we reverse the action and unload it
            return self.cb_unload(NULLOP, modulename)
        else:
            x = self.load(modulename, options=options,
                          increment_refcnt_if_loaded=1)

    @trace
    def cb_unload(self, mode, modulename):
        assert_known_mode(mode)
        if mode == LOAD:
            InstructionLogger.append('unload({0!r})'.format(modulename))
        if mode == UNLOAD:
            # We are in unload mode and the module was requested to be
            # unloaded. But, we don't know if it was previously loaded. So we
            # skip
            return None
        else:
            loaded = self.get_loaded_modules(names_and_short_names=True)
            module = loaded.get(modulename)
            if module is None:
                return None

            lm_refcnt = str2dict(self.environ.get(LM_REFCNT_KEY()))
            if lm_refcnt[module.fullname] > 1:
                # Don't unload, just decrement the reference count
                lm_refcnt[module.fullname] -= 1
                self.environ[LM_REFCNT_KEY()] = dict2str(lm_refcnt)
                return

            self.execmodule(UNLOAD, module)
            return None

    @trace
    def cb_is_loaded(self, modulename):
        InstructionLogger.append('is_loaded({0!r})'.format(modulename))
        return self.is_loaded(modulename)

    @trace
    def cb_use(self, dirname, append=False):
        return self.use(dirname, append=append)

    @trace
    def cb_unuse(self, dirname):
        return self.unuse(dirname)

    @trace
    def cb_source(self, mode, filename):
        """Source a script"""
        key = 'PYMOD_SOURCED_FILES'
        is_sourced = split(self.environ.get(key))
        if mode == LOAD and filename not in is_sourced:
            if not os.path.isfile(filename):
                logging.error('{0}: no such file to source'.format(filename))
            command = self.shell.source_command(filename)
            is_sourced.append(filename)
            self.environ[key] = os.pathsep.join(is_sourced)
            sys.stdout.write(command + ';\n')

    @trace
    def save_collection(self, name, isolate=False):
        loaded = self.get_loaded_modules()
        module_opts = self.environ.get_loaded_modules('opts')
        self.collections.save(name, loaded, module_opts, isolate=isolate)

    @trace
    def remove_collection(self, name):
        self.collections.remove(name)

    @trace
    def restore_collection(self, name, warn_if_missing=True):

        if name == 'system':
            name = DEFAULT_SYS_COLLECTION_NAME

        collection = self.collections.get(name)
        if collection is None:
            if warn_if_missing:
                if name == DEFAULT_SYS_COLLECTION_NAME:
                    msg = 'System default collection does not exist'
                else:
                    msg = 'Collection {0!r} does not exist'.format(name)
                logging.warning(msg)
            return None

        # First unload all loaded modules
        loaded = self.get_loaded_modules(reverse=True)
        for module in loaded:
            self.execmodule(UNLOAD, module)

        # Now load the collection, one module at a time
        for (directory, modules) in collection:
            self.use(directory, append=True)
            for m_dict in modules:
                module = self.modulepath.get_module_by_filename(m_dict['filename'])
                if module is None:
                    msg = 'Saved module {0!r} does not exist ({1})'.format(m_dict['name'], m_dict['filename'])
                    if cfg.stop_on_error:
                        logging.error(msg)
                    else:
                        logging.warning(msg)
                        continue
                if m_dict['options']:
                    self.set_moduleopts(module, m_dict['options'])
                self.execmodule(LOAD, module)
        return None

    @trace
    def restore(self, name, warn_if_missing=True):
        self.restore_collection(name, warn_if_missing=warn_if_missing)

    @trace
    def load(self, modulename, options=None, increment_refcnt_if_loaded=0,
             do_not_register=False, insert_at=None):
        """Load the module given by `modulename`"""

        # Execute the module
        module = self.get_module(modulename)
        if module is None:
            # is it a collection?
            if modulename in self.collections:
                return self.restore_collection(modulename)
            else:
                raise ModuleNotFoundError(modulename, self.modulepath)

        if options:
            self.set_moduleopts(module, options)

        if module.is_loaded:
            if increment_refcnt_if_loaded:
                lm_refcnt = str2dict(self.environ.get(LM_REFCNT_KEY()))
                lm_refcnt[module.fullname] += 1
                self.environ[LM_REFCNT_KEY()] = dict2str(lm_refcnt)
            else:
                msg = '{0} is already loaded, use {1!r} to load again'
                logging.warning(msg.format(module.fullname, 'module reload'))
            return None

        if insert_at is None:
            return self._load(module, do_not_register=do_not_register)

        my_opts = {}
        loaded = self.get_loaded_modules()
        to_unload_and_reload = loaded[(insert_at)-1:]
        for other in to_unload_and_reload[::-1]:
            my_opts[other.fullname] = self.environ.get_loaded_modules('opts', module=other)
            self.execmodule(UNLOAD, other)

        returncode = self._load(module, do_not_register=do_not_register)

        # Reload any that need to be unloaded first
        for other in to_unload_and_reload:
            this_module = self.modulepath.get_module_by_filename(other.filename)
            if this_module is None:
                m_tmp = self.modulepath.get_module_by_name(other.name)
                if m_tmp is not None:
                    this_module = m_tmp
                else:
                    # The only way this_module is None is if inserting
                    # caused a change to MODULEPATH making this module
                    # unavailable.
                    on_mp_changed = self.m_state_changed.setdefault('MP', {})
                    on_mp_changed.setdefault('U', []).append(other)
                    continue

            if this_module.filename != other.filename:
                on_mp_changed = self.m_state_changed.setdefault('MP', {})
                on_mp_changed.setdefault('Up', []).append((other, this_module))

            # Check for module options to set.  If they were not explicitly set
            # on the command line, set them from the previously loaded version
            if not self.moduleopts.get(this_module.fullname):
                self.moduleopts[this_module.fullname] = my_opts[other.fullname]
            self.execmodule(LOAD, this_module)

        return returncode

    @trace
    def is_loaded(self, modulename):
        module = self.get_module(modulename)
        if module is None:
            return False
        return module.is_loaded

    @trace
    def loadfile(self, filename):
        """Load the module by file `filename`"""
        # Execute the module
        module = self.modulepath.get_module_by_filename(filename)

        if module is None:
            raise ModuleNotFoundError(filename, self.modulepath)

        if module.is_loaded:
            msg = '{0} is already loaded, use {1!r} to load again'
            logging.warning(msg.format(module.fullname, 'module reload'))
            return

        return self._load(module)

    def _load(self, module, do_not_register=False):
        """Load the module given by `modulename`"""

        # Before loading this module, look for module of same name and unload
        # it if necessary
        loaded = self.get_loaded_modules()
        for (i, other) in enumerate(loaded):
            if other.name == module.name:
                assert other.is_loaded
                self.swap2(other, module)
                key = 'VersionChanged'
                to_swap = [other.fullname, module.fullname]
                self.m_state_changed.setdefault(key, []).append(to_swap)
                return module

        # Now load it
        self.execmodule(LOAD, module, do_not_register=do_not_register)

        return module

    @trace
    def reload(self, modulename):
        """Reload the module given by `modulename`"""
        module = self.modulepath.get_module_by_name(modulename)
        if module is None:
            raise ModuleNotFoundError(modulename, self.modulepath)
        if not module.is_loaded:
            logging.warning('{0} is not loaded!'.format(module.fullname))
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
        logging.warning(msg)
        return None

    @trace
    def purge(self, allow_load_after_purge=True):
        """Purge all modules from environment"""
        loaded = self.get_loaded_modules(reverse=True)
        for module in loaded:
            self.execmodule(UNLOAD, module)
        if allow_load_after_purge and cfg.load_after_purge is not None:
            for modulename in cfg.load_after_purge:
                self.load(modulename)
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
    def use(self, dirname, append=False):
        """Add dirname to MODULEPATH"""
        if dirname.startswith('~'):
            dirname = os.path.expanduser(dirname)
        if append:
            self.modulepath.append(dirname)
            self.environ[MP_KEY] = self.modulepath.join()
        else:
            lm_files = self.environ.get_loaded_modules('filenames')
            lm_names = self.environ.get_loaded_modules('names')
            bumped = self.modulepath.prepend(dirname) or []
            self.environ[MP_KEY] = self.modulepath.join()
            for m1 in bumped:
                if not m1.is_loaded:
                    continue
                m2 = self.modulepath.get_module_by_name(m1.name)
                if m1.filename != m2.filename:
                    assert m1.is_loaded
                    self.swap2(m1, m2)
                    on_mp_changed = self.m_state_changed.setdefault('MP', {})
                    on_mp_changed.setdefault('Up', []).append((m1, m2))

    @trace
    def unuse(self, dirname):
        """Remove dirname from MODULEPATH"""

        if dirname not in self.modulepath:
            # Nothing to do!
            return

        if dirname.startswith('~'):
            dirname = os.path.expanduser(dirname)

        # Now remove dirname from MODULEPATH
        orphaned = []
        lm_files = self.environ.get_loaded_modules('filenames')
        popped = self.modulepath.remove(dirname)
        if popped is not None:
            for module in popped:
                if module.is_loaded:
                    orphaned.append(module)
            orphaned = sorted(orphaned, key=lambda x: lm_files.index(x.filename))

        for orphan in orphaned[::-1]:
            self.execmodule(UNLOAD, orphan)

        self.environ[MP_KEY] = self.modulepath.join()

        # Now see if any orphans can be reloaded
        for orphan in orphaned:
            m = self.modulepath.get_module_by_filename(orphan.filename)
            if m is None:
                m_tmp = self.modulepath.get_module_by_name(orphan.name)
                if m_tmp is not None:
                    m = m_tmp
                else:
                    # No longer available!
                    on_mp_changed = self.m_state_changed.setdefault('MP', {})
                    on_mp_changed.setdefault('U', []).append(orphan)
                    continue

            # Module of same name still on modulepath
            self.execmodule(LOAD, m)
            on_mp_changed = self.m_state_changed.setdefault('MP', {})
            on_mp_changed.setdefault('Up', []).append((orphan, m))

        return None

    @trace
    def swap(self, module_a_name, module_b_name):
        """Swap modules a and b"""
        module_a = self.modulepath.get_module_by_name(module_a_name)
        module_b = self.modulepath.get_module_by_name(module_b_name)
        if module_a is None:
            raise ModuleNotFoundError(module_a_name, self.modulepath)
        if module_b is None:
            raise ModuleNotFoundError(module_b_name, self.modulepath)
        if not module_a.is_loaded:
            logging.warning('{0} is not loaded, swap not performed!'.format(
                module_a.fullname))
            return
        if module_b.is_loaded:
            logging.warning('{0} is already loaded!'.format(module_b.fullname))
            return
        assert module_a.is_loaded
        self.swap2(module_a, module_b)

        self.m_state_changed.setdefault('Swapped', []).append(
            [module_a.fullname, module_b.fullname])
        return None

    @trace
    def swap2(self, module_a, module_b, options_b=None, maintain_state=0):
        """The general strategy of swapping is to unload all modules in reverse
        order back to the module to be swapped.  That module is then unloaded
        and its replacement loaded.  Afterward, modules that were previously
        unloaded are reloaded.

        On input:
          module_a is loaded
          module_b is not loaded

        On output:
          module_a is not loaded
          module_b is loaded

        The condition that module_b is not loaded on input is not strictly true
        In the case that a module is reloaded, module_a and module_b would be
        the same, so module_b would also be loaded.

        """

        assert module_a.is_loaded

        # Before swapping, unload modules and later reload
        loaded = self.get_loaded_modules()
        for (i, other) in enumerate(loaded):
            if other.name == module_a.name:
                # All modules coming after this one will be unloaded and
                # reloaded
                to_unload_and_reload = loaded[i:]
                break
        else:
            raise Exception('Should have found module_a to swap')

        # Unload any that need to be unloaded first
        my_opts = {}
        for other in to_unload_and_reload[::-1]:
            my_opts[other.fullname] = self.environ.get_loaded_modules('opts', module=other)
            self.execmodule(UNLOAD, other)
        assert other.name == module_a.name

        # Now load it
        if options_b:
            self.set_moduleopts(module_b, options_b)
        self.execmodule(LOAD, module_b)

        # Reload any that need to be unloaded first
        for other in to_unload_and_reload[1:]:
            if maintain_state:
                this_module = self.modulepath.get_module_by_filename(other.filename)
            else:
                this_module = self.modulepath.get_module_by_name(other.fullname)
            if this_module is None:
                m_tmp = self.modulepath.get_module_by_name(other.name)
                if m_tmp is not None:
                    this_module = m_tmp
                else:
                    # The only way this_module is None is if a swap of modules
                    # caused a change to MODULEPATH making this module
                    # unavailable.
                    on_mp_changed = self.m_state_changed.setdefault('MP', {})
                    on_mp_changed.setdefault('U', []).append(other)
                    continue

            if this_module.filename != other.filename:
                on_mp_changed = self.m_state_changed.setdefault('MP', {})
                on_mp_changed.setdefault('Up', []).append((other, this_module))

            # Check for module options to set.  If they were not explicitly set
            # on the command line, set them from the previously loaded version
            if not self.moduleopts.get(this_module.fullname):
                self.moduleopts[this_module.fullname] = my_opts[other.fullname]
            self.execmodule(LOAD, this_module)

        return module_b

    @trace
    def dump(self, stream=None):
        """Dump the final results to the shell to be evaluated"""

        # determine which environment variables to dump
        envars = []
        for (key, val) in self.environ.items():
            if val is None:
                # will be unset
                envars.append(key)
            elif key not in self.environ.ini:
                envars.append(key)
            elif val != self.environ.ini[key]:
                envars.append(key)
        envars = sorted(set(envars))
        alias_names = sorted(self.aliases.keys())
        function_names = sorted(self.shell_functions.keys())

        if not any([envars, alias_names, function_names]):
            logging.debug('Nothing to dump')
            return 0

        s = self.shell.dump(envars, self.environ, alias_names, self.aliases,
                            function_names, self.shell_functions)

        if stream is None:
            return s

        if self.dryrun:
            logging.info(s)
            return 0

        if self.shell.name == 'python':
            sys.stderr.write(s)
        else:
            stream.write(s)

        self.report_changed_module_state()

        return None

    @trace
    def edit_collection(self, name):  # pragma: no cover
        """Edit the collection"""
        import tempfile
        from subprocess import call
        collection = self.collections.get(name)
        if collection is None:
            logging.warning('{0!r} is not a collection'.format(name))
            return
        snew = edit_string_in_vim(json.dumps(collection, default=serialize, indent=2))
        self.collections[name] = json.loads(snew)

    @trace
    def show_available_collections(self, terse=False, regex=None,
                                   stream=sys.stderr):
        s = self.collections.describe(terse=terse, regex=regex)
        stream.write(s)
        return None

    @trace
    def show_collection(self, name, stream=sys.stderr):
        """Show the high-level commands executed by

            module show <collection>
        """
        collection = self.collections.get(name)
        if collection is None:
            logging.warning('{0!r} is not a collection'.format(name))
            return

        loaded = self.environ.get_loaded_modules('names', reverse=True)
        for m in loaded:
            stream.write("unload('{0}')\n".format(m))

        text = []
        for (directory, modules) in collection:
            text.append("use('{0}')".format(directory))
            for module in modules:
                m = create_module_from_kwds(**module)
                name = m.fullname
                opts = module['options']
                if opts:
                    s = "load('{0}', options={1!r})".format(name, opts)
                else:
                    s = "load('{0}')".format(name)
                text.append(s)
        pager('\n'.join(text)+'\n', plain=True)
        return 0

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
    def show_loaded_modules(self, terse=False, regex=None, show_command=False):

        def cat(m):
            opts = loaded_opts.get(m)
            if not opts:
                return m
            return m+''.join(opts)

        loaded = self.environ.get_loaded_modules('names')
        loaded_opts = self.environ.get_loaded_modules('opts')
        loaded_modules = [cat(m) for m in loaded]

        if not loaded_modules:
            logging.info('No loaded modules')
            return

        if terse:
            s = '\n'.join(x.strip() for x in loaded_modules)
            if regex is not None:
                s = grep_pat_in_string(s, regex)
            logging.info(s)
            return

        elif show_command:
            s = '\n'.join('module load {0}'.format(x.strip()) for x in loaded_modules)
            logging.info(s)
            return

        _, width = get_console_dims()
        logging.info('\nCurrently loaded modules:')
        s = wrap2(loaded_modules, width, numbered=1)
        if regex is not None:
            s = grep_pat_in_string(s, regex)
        logging.info(s, end='\n\n')

    @trace
    def set_envar(self, key, value, stream=sys.stdout):
        """Set environment variables manually."""
        kwds = {}
        kwds[key] = value
        s = self.shell.dump(kwds.keys(), kwds)
        if self.dryrun:
            logging.info(s)
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
            logging.error('Module {0!r} has unknown module type: '
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
            'log_message': self.wrap_mf_logging_info(mode, module.filename),
            'log_info': self.wrap_mf_logging_info(mode, module.filename),
            'log_warning': self.wrap_mf_logging_warning(mode, module.filename),
            'log_error': self.wrap_mf_logging_error(mode, module.filename),
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
        #    logging.error(msg)

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
                    logging.warning('Command {0!r} failed'.format(command))
            return
        return mf_execute

    def wrap_mf_logging_info(self, mode, filename):
        @trace(name='log_message')
        def mf_logging_info(message):
            logging.info(message, filename)
        return mf_logging_info

    def wrap_mf_logging_warning(self, mode, filename):
        @trace(name='log_warning')
        def mf_logging_warning(message):
            logging.warning(message, filename)
        return mf_logging_warning

    def wrap_mf_logging_error(self, mode, filename):
        @trace(name='log_error')
        def mf_logging_error(message, noraise=0):
            noraise = noraise or self.load_for_show
            logging.error(message, filename, noraise=noraise)
        return mf_logging_error

    # ---------------- FUNCTIONS THAT MODIFY THE ENVIRONMENT ---------------- #
    @InstructionLogger.log_instruction
    def setenv(self, name, value, **kwds):
        """Set value of environment variable `name`"""
        if name == 'MODULEPATH':
            logging.error('MODULEPATH cannot be set by setenv')
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
            logging.error('MODULEPATH cannot be unset by unsetenv')
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
        logging.error('One of the prerequisites {0!r} must '
                      'first be loaded'.format(modulenames))

    @InstructionLogger.log_instruction
    def prereq(self, *modulenames):
        if self.load_for_show:
            return
        loaded = self.get_loaded_modules(names_and_short_names=True)
        for modulename in modulenames:
            if modulename in loaded:
                continue
            logging.error('Prerequisite {0!r} must '
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
                    logging.error(msg.format(name=name, modulename=modulename))

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


    @trace
    def family(self, mode, family_name, module):
        """Assign a family"""

        name = module.name
        version = module.version
        module.family = family_name
        def family_envar_keys():
            key1 = 'MODULE_FAMILY_{0}'.format(family_name.upper())
            key2 = 'MODULE_FAMILY_{0}_VERSION'.format(family_name.upper())
            return (key1, key2)

        InstructionLogger.append('family({0!r})'.format(family_name))
        if mode in (LOAD,):
            key1, key2 = family_envar_keys()
            if self.environ.get(key1) is not None:
                # Attempting to load module of same family
                x, v = self.environ[key1], self.environ[key2]
                other = x if v in ('false', None) else os.path.join(x, v)
                raise FamilyLoadedError(other)
            self.setenv(key1, name)
            self.setenv(key2, 'false' if version is None else version)

        elif mode in (UNLOAD,):
            key1, key2 = family_envar_keys()
            self.unsetenv(key1)
            self.unsetenv(key2)

        else:
            # in all other modes, setenv is a null op
            pass

    def read_clones(self, filename):
        if os.path.isfile(filename):
            return dict(json.load(open(filename)))
        return {}

    @trace
    def clone_current_environment(self, name):
        env = self.shell.filter_environ(self.environ)
        filename = cfg.clones_filename
        clones = self.read_clones(filename)
        clones[name] = [(key, val) for (key, val) in env.items()]
        with open(filename, 'w') as fh:
            json.dump(clones, fh, default=serialize, indent=2)
        return

    @trace
    def restore_clone(self, name):
        filename = cfg.clones_filename
        clones = self.read_clones(filename)
        if name not in clones:
            logging.error('{0!r} is not a cloned environment'.format(name))
        the_clone = dict(clones[name])

        # Purge current environment
        self.purge(allow_load_after_purge=False)
        self.modulepath.reset(directories=the_clone[MP_KEY].split(os.pathsep))

        # Make sure environment matches clone
        for (key, val) in the_clone.items():
            self.environ[key] = val

        # Load modules to make sure aliases/functions are restored
        module_files = split(the_clone[LM_FILES_KEY], os.pathsep)
        module_opts = str2dict(the_clone[LM_OPTS_KEY])

        for (i, filename) in enumerate(module_files):
            module = self.modulepath.get_module_by_filename(filename)
            if module is None:
                raise ModuleNotFoundError(filename, self.modulepath)
            self.set_moduleopts(module, module_opts[module.fullname])
            self.execmodule(LOAD_PARTIAL, module, do_not_register=True)

    @trace
    def remove_clone(self, name):
        filename = cfg.clones_filename
        clones = self.read_clones(filename)
        clones.pop(name, None)
        with open(filename, 'w') as fh:
            json.dump(clones, fh, default=serialize, indent=2)
        return

    @trace
    def display_clones(self, terse=False, stream=sys.stderr):
        string = []
        filename = cfg.clones_filename
        clones = self.read_clones(filename)
        names = sorted([x for x in clones.keys()])
        if not terse:
            _, width = get_console_dims()
            if not names:
                s = '(None)'.center(width)
            else:
                s = wrap2(names, width)
            string.append(s+'\n')
        else:
            if names:
                string.append('\n'.join(c for c in names))

        string = '\n'.join(string)
        stream.write(string)
