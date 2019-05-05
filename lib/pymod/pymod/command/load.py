import os
import sys
import argparse

import contrib.util.logging as logging
import pymod.shell
import pymod.modulepath
from pymod.command.common import parse_module_options
from pymod.error import ModuleNotFoundError

description = 'Load modules into environment'
level = 'short'
section = 'module'


def setup_parser(subparser):
    """Parser is only constructed so that this prints a nice help
       message with -h. """
    subparser.add_argument(
        '-x', dest='do_not_register',
        action='store_true', default=False,
        help='Do not register module in LOADEDMODULES')
    subparser.add_argument(
        '-i', '--insert-at', type=int, default=None,
        help='Load the module as the `i`th module.')
    subparser.add_argument(
        'args', nargs=argparse.REMAINDER,
        help=('Modules and options to load. Additional options can be sent \n'
              'directly to the module using the syntax, `+option[=value]`. \n'
              'See the module options help for more details.'))


def _load(modulename, options, do_not_register=False, insert_at=None,
          increment_refcnt_if_loaded=True):
    """Load the module given by `modulename`"""

    # Execute the module
    module = pymod.modulepath.get(modulename)
    # FIXME: finish
    print(module)
    return 0

    if module is None:
        # is it a collection?
        if pymod.collections.is_collection(modulename):
            return pymod.collections.restore(modulename)
        else:
            raise ModuleNotFoundError(modulename, mp=pymod.modulepath)

    if options:
        module.set_argv(options)

    if module.is_loaded:
        if increment_refcnt_if_loaded:
            lm_refcnt = str2dict(self.environ.get(LM_REFCNT_KEY()))
            lm_refcnt[module.fullname] += 1
            self.environ[LM_REFCNT_KEY()] = dict2str(lm_refcnt)
        else:
            msg = '{0} is already loaded, use {1!r} to load again'
            logging.warn(msg.format(module.fullname, 'module reload'))
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

def load(parser, args):
    argv = parse_module_options(args.args)
    for (name, opts) in argv:
        _load(name, opts, args.do_not_register, args.insert_at)
    pymod.shell.dump()
    return 0
