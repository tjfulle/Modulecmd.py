import pymod.modulepath
import pymod.mc

from pymod.mc.execmodule import execmodule
from pymod.error import ModuleNotFoundError
import contrib.util.logging as logging


def load(modulename, options, do_not_register=False, insert_at=None,
         increment_refcnt_if_loaded=False):
    """Load the module given by `modulename`"""

    # Execute the module
    logging.verbose('Loading {}'.format(modulename))
    module = pymod.modulepath.get(modulename)

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
        return 0

    if insert_at is None:
        return load_impl(module, do_not_register=do_not_register)

    return load_inserted(module, insert_at)


def load_inserted(module, insert_at):
    """Load the `module` at `insert_at` by unloading all modules beyond
    `insert_at`, loading `module`, then reloading the unloaded modules"""

    raise NotImplementedError('trying to load {0} but mc.load_inserted is '
                              'not yet implemented'.format(module))

    my_opts = {}
    loaded = self.get_loaded_modules()
    to_unload_and_reload = loaded[(insert_at)-1:]
    for other in to_unload_and_reload[::-1]:
        my_opts[other.fullname] = self.environ.get_loaded_modules('opts', module=other)
        execmodule(other, 'unload')

    return_module = load_impl(module, do_not_register=do_not_register)

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
        execmodule(this_module, 'load')

    return return_module

def load_impl(module, do_not_register=False):
    """Load the module given by `modulename`"""

    # Before loading this module, look for module of same name and unload
    # it if necessary

    # See if a module of the same name is already loaded. If so, swap that
    # module with the requested module
    for (i, other) in enumerate(pymod.mc.loaded_modules()):
        if other.name == module.name:
            pymod.mc.swap_impl(other, module)
            pymod.mc.register_changed_version(other, module)
            return module

    # Now load it
    execmodule(module, 'load', do_not_register=do_not_register)

    raise NotImplementedError('trying to load {0} but mc.load_impl is '
                              'not yet implemented'.format(module))

    return module
