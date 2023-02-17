import os
import sys

import modulecmd.alias
import modulecmd.callback
import modulecmd.clone
import modulecmd.collection
import modulecmd.config
import modulecmd.environ
import modulecmd.error
import modulecmd.modes
import modulecmd.module
import modulecmd.modulepath
import modulecmd.names
import modulecmd.paths
import modulecmd.shell
import modulecmd.user
from modulecmd.util import working_dir, singleton, terminal_size, colify, colorize

import llnl.util.tty as tty
from modulecmd.error import (
    FamilyLoadedError,
    ModuleConflictError,
    ModuleLoadError,
    ModuleNotFoundError,
    ModuleNotLoadedError,
    PrereqMissingError,
)
from modulecmd.xio import pager
from modulecmd.util import split, grep_pat_in_string
from six import StringIO, exec_


builtin_list = list


class system_state:
    def __init__(self):
        self.cur_module_command_his = StringIO()
        self._loaded_modules = None
        self._initial_loaded_modules = None
        self._swapped_explicitly = []
        self._swapped_on_version_change = []
        self._swapped_on_family_update = []
        self._swapped_on_mp_change = []
        self._unloaded_on_mp_change = []

    def module_is_loaded(self, key):
        if isinstance(key, modulecmd.module.Module):
            return key in self.loaded_modules
        elif os.path.isfile(key):
            return key in [m.filename for m in self.loaded_modules]
        else:
            for module in self.loaded_modules:
                if module.name == key or module.fullname == key:
                    return True
        return False

    @property
    def loaded_modules(self):
        if self._loaded_modules is None:
            tty.debug("Reading loaded modules")
            self._loaded_modules = []
            lm_cellar = modulecmd.environ.get(
                modulecmd.names.loaded_module_cellar, default=[], serialized=True
            )
            for ar in lm_cellar:
                module = unarchive_module(ar)
                self._loaded_modules.append(module)
            self._initial_loaded_modules = [m.fullname for m in self._loaded_modules]
        # return copy so that no one else can modify the loaded modules
        return builtin_list(self._loaded_modules)

    @loaded_modules.setter
    def loaded_modules(self, modules):
        """Set environment variables for loaded module names and files"""
        self._loaded_modules = modules
        self.update_module_stat()

    def append_module(self, module):
        self._loaded_modules.append(module)
        self.update_module_stat()

    def update_module_stat(self):
        assert all([m.acquired_as is not None for m in self._loaded_modules])
        lm = [m.asdict() for m in self._loaded_modules]
        modulecmd.environ.set(modulecmd.names.loaded_module_cellar, lm, serialize=True)

        # The following are for compatibility with other module programs
        lm_names = [m.fullname for m in self._loaded_modules]
        modulecmd.environ.set_path(modulecmd.names.loaded_modules, lm_names)

        lm_files = [m.filename for m in self._loaded_modules]
        modulecmd.environ.set_path(modulecmd.names.loaded_module_files, lm_files)

    def register_module(self, module):
        """Register the `module` to the list of loaded modules"""
        # Update the environment
        if not modulecmd.modulepath.contains(module.modulepath):
            raise modulecmd.error.InconsistentModuleStateError(module)
        if modulecmd.config.get("skip_add_devpack") and module.name.startswith(
            ("sems-devpack", "devpack")
        ):
            return
        if module not in self.loaded_modules:
            module.refcount += 1
            self.append_module(module)
        else:
            raise ModuleRegisteredError(module)

    def unregister_module(self, module):
        """Unregister the `module` to the list of loaded modules"""
        # Don't use `self.loaded_modules` because the module we are unregistering
        # may no longer be available. `self.loaded_modules` makes some assumptions
        # that can be violated in certain situations. Like, for example, # when
        # "unusing" a directory on the MODULEPATH which has loaded modules.
        # Those modules are automaically unloaded since they are no longer
        # available.
        for (i, loaded) in enumerate(self.loaded_modules):
            if loaded.filename == module.filename:
                break
        else:
            raise ModuleNotRegisteredError(module)
        module.refcount = 0
        self._loaded_modules.pop(i)

    def swapped_explicitly(self, old, new):
        self._swapped_explicitly.append((old, new))

    def swapped_on_version_change(self, old, new):
        self._swapped_on_version_change.append((old, new))

    def swapped_on_mp_change(self, old, new):
        self._swapped_on_mp_change.append((old, new))

    def unloaded_on_mp_change(self, old):
        self._unloaded_on_mp_change.append(old)

    def swapped_on_family_update(self, old, new):
        self._swapped_on_family_update.append((old, new))

    def format_changes(self, file=None):
        fown = file is None
        file = file or StringIO()
        self.format_loaded(file=file)
        self.format_swapped(file=file)
        self.format_updated_f(file=file)
        self.format_updated_v(file=file)
        self.format_unloaded_mp(file=file)
        self.format_updated_mp(file=file)
        if fown:
            return file.getvalue()

    def format_loaded(self, file=None):
        file = file or StringIO()
        if self._loaded_modules is not None and modulecmd.config.get("verbose"):
            new_modules = [
                m
                for m in self._loaded_modules
                if m.fullname not in self._initial_loaded_modules
            ]
            if new_modules:
                file.write("The following modules were @G{loaded}\n")
                for (i, m) in enumerate(new_modules):
                    file.write("  {0}) {1}\n".format(i + 1, m.fullname))
                file.write("\n")

    def format_swapped(self, file=None):
        file = file or StringIO()
        # Report swapped
        if self._swapped_explicitly:
            file.write("The following modules have been @G{swapped}\n")
            for (i, (m1, m2)) in enumerate(self._swapped_explicitly):
                a, b = m1.fullname, m2.fullname
                file.write("  {0}) {1} => {2}\n".format(i + 1, a, b))
            file.write("\n")

    def format_updated_f(self, file=None):
        file = file or StringIO()
        # Report reloaded
        if self._swapped_on_family_update:  # pragma: no cover
            file.write(
                "The following modules in the same family have "
                "been @G{updated with a version change}\n"
            )
            for (i, (m1, m2)) in enumerate(self._swapped_on_family_update):
                a, b, fam = m1.fullname, m2.fullname, m1.family
                file.write("  {0}) {1} => {2} ({3})\n".format(i + 1, a, b, fam))
            file.write("\n")

    def format_updated_v(self, file=None):
        file = file or StringIO()
        if self._swapped_on_version_change:
            file.write(
                "The following modules have been @G{updated with a version change}\n"
            )
            for (i, (m1, m2)) in enumerate(self._swapped_on_version_change):
                a, b = m1.fullname, m2.fullname
                file.write("  {0}) {1} => {2}\n".format(i + 1, a, b))
            file.write("\n")

    def format_unloaded_mp(self, file=None):
        file = file or StringIO()
        # Report changes due to to change in modulepath
        if self._unloaded_on_mp_change:  # pragma: no cover
            lm_files = [_.filename for _ in self.loaded_modules]
            unloaded = [
                _ for _ in self._unloaded_on_mp_change if _.filename not in lm_files
            ]
            file.write(
                "The following modules have been @G{unloaded with a MODULEPATH change}\n"
            )
            for (i, m) in enumerate(unloaded):
                file.write("  {0}) {1}\n".format(i + 1, m.fullname))
            file.write("\n")

    def format_updated_mp(self, file=None):
        file = file or StringIO()
        debug_mode = modulecmd.config.get("debug")
        if self._swapped_on_mp_change:
            file.write(
                "The following modules have been @G{updated with a MODULEPATH change}\n"
            )
            for (i, (m1, m2)) in enumerate(self._swapped_on_mp_change):
                a, b = m1.fullname, m2.fullname
                if debug_mode:  # pragma: no cover
                    n = len("  {0}) ".format(i + 1))
                    a += " ({0})".format(m1.modulepath)
                    b = "\n" + " " * n + b + " ({0})".format(m2.modulepath)
                file.write("  {0}) {1} => {2}\n".format(i + 1, a, b))
            file.write("\n")

        return


state = system_state()


def module_is_loaded(key):
    return state.module_is_loaded(key)


def loaded_modules():
    return state.loaded_modules


def register_module(module):
    return state.register_module(module)


def unregister_module(module):
    return state.unregister_module(module)


def unarchive_module(ar):
    path = ar.get("modulepath")
    if path and not modulecmd.modulepath.contains(path):  # pragma: no cover
        use(path)
    module = modulecmd.modulepath.get(ar["filename"])
    if module is None:
        raise modulecmd.error.ModuleNotFoundError(ar["fullname"])
    assert module.fullname == ar["fullname"]
    module.family = ar["family"]
    module.opts = ar["opts"]
    module.acquired_as = ar["acquired_as"]
    module.refcount = ar["refcount"]
    return module


def avail(terse=False, regex=None, show_all=False, long_format=False):
    avail = modulecmd.modulepath.avail(
        terse=terse, regex=regex, long_format=long_format
    )
    if show_all:
        avail += modulecmd.collection.avail(terse=terse, regex=regex)
        avail += modulecmd.clone.avail(terse=terse)
    return avail


def save_clone(name):
    return modulecmd.clone.save(name)


def restore_clone(name):
    the_clone = modulecmd.clone.get(name)
    if the_clone is None:
        raise modulecmd.error.CloneDoesNotExistError(name)
    restore_clone_impl(the_clone)


def remove_clone(name):
    return modulecmd.clone.remove(name)


def restore_clone_impl(the_clone):
    # Purge current environment
    purge(load_after_purge=False)

    mp = the_clone.pop(modulecmd.names.modulepath, None)
    current_env = modulecmd.environ.copy(include_os=True)
    for (key, val) in current_env.items():
        if key == modulecmd.names.modulepath:
            continue
        modulecmd.environ.unset(key)

    path = modulecmd.modulepath.Modulepath(split(mp, os.pathsep))
    modulecmd.modulepath.set_path(path)

    # Make sure environment matches clone
    for (key, val) in the_clone.items():
        modulecmd.environ.set(key, val)

    # Load modules to make sure aliases/functions are restored
    lm_cellar = modulecmd.environ._get_and_deserialize(
        the_clone, modulecmd.names.loaded_module_cellar
    )
    if lm_cellar:
        loaded_modules = []
        for ar in lm_cellar:
            try:
                module = unarchive_module(ar)
            except modulecmd.error.ModuleNotFoundError:
                raise modulecmd.error.CloneModuleNotFoundError(
                    ar["fullname"], ar["filename"]
                )
            loaded_modules.append(module)
        state.loaded_modules = loaded_modules

        for module in loaded_modules:
            load_partial(module)


def save_collection(name):
    """Save currently loaded modules to a collection"""
    modulecmd.collection.save(name, state.loaded_modules)


def show_collection(name):
    """Save the collection `name`"""
    s = modulecmd.collection.show(name)
    sys.stderr.write(s + "\n")
    return 0


def restore_collection(name):
    """Restore a collection of modules previously saved"""
    the_collection = modulecmd.collection.get(name)
    if the_collection is None:
        raise modulecmd.error.CollectionNotFoundError(name)
    return restore_collection_impl(name, the_collection)


def remove_collection(name):
    """Delete collection `name` from database"""
    modulecmd.collection.remove(name)


def pop_from_loaded_collection(name):
    """Remove module `name` from currently loaded collection"""
    modulecmd.collection.pop_from_loaded_collection(name)


def add_to_loaded_collection(name):
    """Append module `name` to currently loaded collection"""
    modulecmd.collection.add_to_loaded_collection(name)


def restore_collection_impl(name, the_collection):
    # First unload all loaded modules
    modulecmd.environ.unset(modulecmd.names.loaded_collection)
    purge(load_after_purge=False)

    # clear the modulepath
    orig_path = modulecmd.modulepath.path()
    path = modulecmd.modulepath.Modulepath([])
    modulecmd.modulepath.set_path(path)

    # Now load the collection, one module at a time
    for (directory, archives) in the_collection:
        use(directory, append=True)
        for ar in archives:
            try:
                module = unarchive_module(ar)
                tty.verbose("Loading part of collection: {0}".format(module))
            except modulecmd.error.ModuleNotFoundError:
                raise modulecmd.error.CollectionModuleNotFoundError(
                    ar["fullname"], ar["filename"]
                )
            load_impl(module)
            module.acquired_as = module.fullname
            assert module.is_loaded
    modulecmd.environ.set(modulecmd.names.loaded_collection, name)
    for p in orig_path:
        if not modulecmd.modulepath.contains(p):  # pragma: no cover
            use(p, append=True)
    return None


def conflict(module, *conflicting):
    """The module we are trying to load, `module` conflicts with the module
    given by `conflicting_module`"""
    loaded_modules = state.loaded_modules
    lm_names = builtin_list(
        set([x for m in loaded_modules for x in [m.name, m.fullname]])
    )
    for other in conflicting:
        if other in lm_names:
            if modulecmd.config.get("resolve_conflicts"):
                # Unload the conflicting module
                unload(other)
            else:
                raise ModuleConflictError(other, module.name)


def get_entity_text(name):
    module = modulecmd.modulepath.get(name)
    if module is not None:
        return open(module.filename).read()
    elif modulecmd.collection.contains(name):
        return str(modulecmd.collection.get(name))
    raise modulecmd.error.EntityNotFoundError(name)


def more(name):
    pager(get_entity_text(name))


def cat(name):
    pager(get_entity_text(name), plain=True)


def format_output():  # pragma: no cover
    """Format the final output for the shell to be evaluated"""
    output = modulecmd.environ.format_output()
    return output


def dump(stream=None):  # pragma: no cover
    """Dump the final results to the shell to be evaluated"""
    output = format_output()
    stream = sys.stderr if modulecmd.config.get("dryrun") else stream or sys.stdout
    stream.write(output)

    output = state.format_changes()
    if output.split():
        sys.stderr.write(colorize(output))


# ----------------------------- MODULE EXECUTION FUNCTIONS
def execmodule(module, mode):
    """Execute the module in a sandbox"""
    assert module.acquired_as is not None
    modulecmd.modes.assert_known_mode(mode)

    # Enable logging of commands in this module
    state.cur_module_command_his = StringIO()

    try:
        return execmodule_in_sandbox(module, mode)

    except FamilyLoadedError as e:
        # Module of same family already loaded, unload it first

        # This comes after first trying to load the module because the
        # family is set within the module, so the module must first be
        # loaded to determine the family. If when the family is being set
        # it is discovered that a module from the same family is loaded,
        # the FamilyLoadedError is raised.

        # This should only happen in load mode
        assert mode == modulecmd.modes.load
        other = modulecmd.modulepath.get(e.args[0])
        state.swapped_on_family_update(other, module)
        assert other.is_loaded
        swap_impl(other, module)


def execmodule_in_sandbox(module, mode):
    """Execute python module in sandbox"""

    # Execute the environment
    tty.debug("Executing module {0} with mode {1}".format(module, mode))
    module.prepare()
    ns = module_exec_sandbox(module, mode)
    code = compile(module.read(mode), module.filename, "exec")
    with working_dir(os.path.dirname(module.filename)):
        try:
            if isinstance(module, modulecmd.module.TclModule):
                clone = modulecmd.environ.clone()
            exec_(code, ns, {})
        except modulecmd.error.StopLoadingModuleError:
            pass
        except modulecmd.error.TclModuleBreakError:
            # `break` command encountered.  we need to roll back changes to the
            # environment and tell whoever called not to register this module
            modulecmd.environ.restore(clone)
            module.exec_failed_do_not_register = True


def module_exec_sandbox(module, mode):
    callback = lambda cb, **kwds: modulecmd.callback.callback(cb, module, mode, **kwds)
    ns = {
        "os": os,
        "sys": sys,
        "env": modulecmd.environ.copy(include_os=True),
        "self": module,
        "user_env": modulecmd.user.env,
        "is_darwin": "darwin" in sys.platform,
        "IS_DARWIN": "darwin" in sys.platform,
        #
        "add_option": module.add_option,
        "opts": singleton(module.parse_opts),
    }

    for fun in modulecmd.callback.all_callbacks():
        kwds = {}
        if fun.endswith(("set_alias", "set_shell_function", "getenv")):
            # when='always' because we may partially load a module just define
            # aliases and functions.  This is used by the clone capability that
            # can set environment variables from a clone, but cannot know what
            # aliases and functions existed in the clone.
            kwds["when"] = "always"
        elif fun == "whatis":
            # filter out this function if not in whatis mode
            kwds["when"] = mode == modulecmd.modes.whatis
        elif fun == "help":
            # filter out this function if not in help mode
            kwds["when"] = mode == modulecmd.modes.help
        else:
            # Let the function know nothing was explicitly set
            kwds["when"] = None
        ns[fun] = callback(fun, **kwds)
    return ns


def family(module, mode, family_name):
    """Assign a family"""

    name = module.name
    version = module.version.string
    module.family = family_name

    def family_envar_keys():
        fam_key = modulecmd.names.family_name(family_name)
        ver_key = modulecmd.names.family_version(family_name)
        return (fam_key, ver_key)

    if mode == modulecmd.modes.unload:
        fam_key, ver_key = family_envar_keys()
        modulecmd.environ.unset(fam_key)
        modulecmd.environ.unset(ver_key)

    else:
        fam_key, ver_key = family_envar_keys()
        fam = modulecmd.environ.get(fam_key)
        if fam is not None:
            # Attempting to load module of same family
            ver = modulecmd.environ.get(ver_key)
            other = fam if ver in ("false", None) else os.path.join(fam, ver)
            raise FamilyLoadedError(other)

        modulecmd.environ.set(fam_key, name)
        ver = "false" if not version else version
        modulecmd.environ.set(ver_key, ver)


def find(names):
    for name in names:
        s = None
        candidates = modulecmd.modulepath.candidates(name)
        if not candidates:
            raise ModuleNotFoundError(name)
        for module in candidates:
            s = "{bold}%s{endc}\n  {cyan}%s{endc}}" % (module.fullname, module.filename)
            sys.stderr.write(colorize(s) + "\n")


def help(modulename):
    """Display 'help' message for the module given by `modulename`"""
    module = modulecmd.modulepath.get(modulename)
    if module is None:
        raise ModuleNotFoundError(modulename, mp=modulecmd.modulepath)
    load_partial(module, mode=modulecmd.modes.help)
    return module.format_help()


def info(names):
    for name in names:
        modules = modulecmd.modulepath.candidates(name)
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
            s += "  {cyan}Filename:{endc}     %s\n" % module.filename
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

            sys.stderr.write(colorize(s) + "\n")


def init(dirnames):
    initial_env = modulecmd.environ.copy(include_os=True)
    if modulecmd.collection.contains(
        modulecmd.names.default_user_collection
    ):  # pragma: no cover
        restore_collection(modulecmd.names.default_user_collection)
    for dirname in dirnames:
        use(dirname, append=True)
    modulecmd.environ.set(modulecmd.names.initial_env, initial_env, serialize=True)
    return


def list(terse=False, show_command=False, regex=None):
    Namespace = modulecmd.module.Namespace
    if not state.loaded_modules:
        return "No loaded modules\n"

    sio = StringIO()
    loaded_module_names = []
    for loaded in state.loaded_modules:
        fullname = loaded.fullname
        if loaded.opts:
            fullname += " " + Namespace(**(loaded.opts)).joined(" ")
        loaded_module_names.append(fullname)

    if terse:
        sio.write("\n".join(loaded_module_names))
    elif show_command:
        for module in loaded_module_names:
            sio.write("module load {0}\n".format(module))
    else:
        sio.write("Currently loaded modules\n")
        loaded = [
            "{0}) {1}".format(i + 1, m) for (i, m) in enumerate(loaded_module_names)
        ]
        width = terminal_size().columns
        output = colify(loaded, indent=4, width=max(100, width))
        sio.write(output + "\n")

    s = sio.getvalue()
    if regex:
        s = grep_pat_in_string(s, regex, color="G")

    return s


def load(name, opts=None, insert_at=None, caller="command_line"):
    """Load the module given by `name`

    This is a higher level interface to `load_impl` that gets the actual module
    object from `name`

    Parameters
    ----------
    name : string_like
        Module name, full name, or file path
    opts : dict
        (Optional) options to send to module
    insert_at : int
        Load the module as the `insert_at`th module.
    caller : str
        Who is calling. If modulefile, the reference count will be incremented
        if the module is already loaded.

    Returns
    -------
    module : Module
        If the `name` was loaded (or is already loaded), return its module.

    Raises
    ------
    ModuleNotFoundError

    """
    tty.verbose("Loading {0}".format(name))

    # Execute the module
    module = modulecmd.modulepath.get(
        name, use_file_modulepath=True
    )  # caller=="command_line")
    if module is None:
        if caller == "command_line":
            collection = modulecmd.collection.get(name)
            if collection is not None:
                return restore_collection_impl(name, collection)
        raise ModuleNotFoundError(name, mp=modulecmd.modulepath)

    # Set the command line options
    if opts:
        module.opts = opts

    if module.is_loaded:
        if caller == "modulefile":
            module.refcount += 1
        else:
            tty.warn(
                "{0} is already loaded, use 'module reload' to reload".format(
                    module.fullname
                )
            )
        return module

    if modulecmd.environ.get(modulecmd.names.loaded_collection):  # pragma: no cover
        collection = modulecmd.environ.get(modulecmd.names.loaded_collection)
        tty.debug(
            "Loading {0} on top of loaded collection {1}. "
            "Removing the collection name from the environment".format(
                module.fullname, collection
            )
        )
        modulecmd.environ.unset(modulecmd.names.loaded_collection)

    if insert_at is not None:
        load_inserted_impl(module, insert_at)
    else:
        load_impl(module)

    return module


def load_impl(module):
    """Implementation of load.

    Parameters
    ----------
    module : Module
        The module to load

    """

    # See if a module of the same name is already loaded. If so, swap that
    # module with the requested module
    for other in state.loaded_modules:
        if other.name == module.name:
            swap_impl(other, module)
            state.swapped_on_version_change(other, module)
            return

    # Now load it
    execmodule(module, modulecmd.modes.load)

    if getattr(module, "exec_failed_do_not_register", False):
        # Something happened during the execution of this module and we are not
        # to register it.
        pass
    elif module.refcount != 0:
        # Nonzero reference count means the module load was completed by
        # someone else. This can only happen in the case of loading a module of
        # the same family. In that case, execmodule catches a FamilyLoadedError
        # exception and swaps this module with the module of the same family.
        # The swap completes the load.
        if not (
            state._swapped_on_family_update
            and module == state._swapped_on_family_update[-1][1]
        ):  # pragma: no cover
            raise ModuleLoadError("Expected 0 refcount")
    else:
        state.register_module(module)

    return


def load_inserted_impl(module, insert_at):
    """Load the `module` at `insert_at` by unloading all modules beyond
    `insert_at`, loading `module`, then reloading the unloaded modules"""

    insertion_loc = insert_at - 1
    to_unload_and_reload = state.loaded_modules[insertion_loc:]
    opts = [m.opts for m in to_unload_and_reload]
    for other in to_unload_and_reload[::-1]:
        unload_impl(other)

    load_impl(module)

    # Reload any that need to be unloaded first
    for (i, other) in enumerate(to_unload_and_reload):
        assert not other.is_loaded
        other_module = modulecmd.modulepath.get(other.acquired_as)
        if other_module is None:
            # The only way this_module is None is if inserting caused a change
            # to MODULEPATH making this module unavailable.
            state.unloaded_on_mp_change(other)
            continue

        if other_module.filename != other.filename:
            state.swapped_on_mp_change(other, other_module)
        else:
            other_module.opts = opts[i]

        load_impl(other_module)

    return


def load_partial(module, mode=None):
    """Implementation of load, but only load partially.

    Parameters
    ----------
    module : Module
        The module to load

    Notes
    -----
    This function is used to do a partial load. A partial load is one in which
    only some of the callback functions are actually executed. This function is
    used, e.g., by restore_clone to load a module, but only execute set_alias
    and set_shell_function.  In fact, that is the only current use case.

    """
    # Execute the module
    if mode is not None:
        assert mode in modulecmd.modes.informational
    mode = mode or modulecmd.modes.load_partial
    execmodule(module, mode)
    return


def _partition(key):
    first, _, last = key.partition(":")
    if not last.split():
        first, last = "name", first
    elif first not in ("family", "name"):
        raise Exception("{0} not a known ID to prereq".format(first))
    return first, last


def prereq_any(*prereqs):
    lm_names = [x for m in state.loaded_modules for x in [m.name, m.fullname]]
    lm_fams = [m.family for m in state.loaded_modules if m.family]
    for prereq in prereqs:
        key, val = _partition(prereq)
        a = lm_fams if key == "family" else lm_names
        if val in a:
            return
    raise PrereqMissingError(*prereqs)


def prereq(*prereqs):
    lm_names = [x for m in state.loaded_modules for x in [m.name, m.fullname]]
    lm_fams = [m.family for m in state.loaded_modules if m.family]
    for prereq in prereqs:
        key, val = _partition(prereq)
        a = lm_fams if key == "family" else lm_names
        if val in a:
            continue
        raise PrereqMissingError(val)


def purge(load_after_purge=True):
    """Purge all modules from environment"""
    for module in state.loaded_modules[::-1]:
        if module.is_loaded:
            unload_impl(module)

    if load_after_purge:
        load_after_purge = modulecmd.config.get("load_after_purge")
        tty.debug(str(load_after_purge))
        if load_after_purge is not None:
            for name in load_after_purge:
                load(name)

    return None


def raw(*commands):
    """Run the commands given in `commands`"""
    for command in commands:
        modulecmd.environ.raw_shell_command(command)


def refresh():
    """Unload all modules from environment and reload them"""
    loaded_modules = state.loaded_modules
    for module in loaded_modules[::-1]:
        tty.verbose("Unloading {0}".format(module))
        if module.is_loaded:
            unload_impl(module)
    for module in loaded_modules:
        tty.verbose("Loading {0}".format(module))
        if not module.is_loaded:
            load_impl(module)


def reload(name):
    """Reload the module given by `modulename`"""
    module = modulecmd.modulepath.get(name)
    if module is None:
        raise ModuleNotFoundError(name, modulecmd.modulepath)
    if not module.is_loaded:
        tty.warn("{0} is not loaded!".format(module.fullname))
        return
    assert module.is_loaded
    swap_impl(module, module, maintain_state=True, caller="reload")
    return module


def reset():
    initial_env = modulecmd.environ.get(modulecmd.names.initial_env, serialized=True)
    restore_clone_impl(initial_env)
    return initial_env


def show(name, opts=None, insert_at=None, mode="load"):
    """Show the commands that would result from loading module given by `name`

    Parameters
    ----------
    name : string_like
        Module name, full name, or file path
    insert_at : int
        Load the module as the `insert_at`th module.

    Raises
    ------
    ModuleNotFoundError

    """
    # Execute the module
    module = modulecmd.modulepath.get(name)
    if module is None:
        raise ModuleNotFoundError(name, mp=modulecmd.modulepath)

    # Set the command line options
    if opts:
        module.opts = opts

    # Now execute it
    execmodule(module, modulecmd.modes.show)

    # and show it
    sys.stderr.write(state.cur_module_command_his.getvalue())


def source(filename, *args):
    """Source the file `filename`"""
    sourced = modulecmd.environ.get_path(modulecmd.names.sourced_files)
    if filename not in sourced:
        # Only source if it hasn't been sourced
        if not os.path.isfile(filename):
            raise ValueError("{0}: no such file to source".format(filename))
        sourced.append(filename)
        modulecmd.environ.set_path(modulecmd.names.sourced_files, sourced)
        modulecmd.environ.source_file(filename, *args)


def swap(module_a_name, module_b_name, caller="command_line"):
    """Swap modules a and b"""
    module_a = modulecmd.modulepath.get(module_a_name)
    module_b = modulecmd.modulepath.get(module_b_name)
    if module_a is None:
        raise ModuleNotFoundError(module_a_name, modulecmd.modulepath)
    if module_b is None:
        raise ModuleNotFoundError(module_b_name, modulecmd.modulepath)
    if module_b.is_loaded:
        tty.warn("{0} is already loaded!".format(module_b.fullname))
        return module_b
    if not module_a.is_loaded:
        return load_impl(module_b)

    assert module_a.is_loaded

    swap_impl(module_a, module_b, caller=caller)
    state.swapped_explicitly(module_a, module_b)

    return module_b


def swap_impl(module_a, module_b, maintain_state=False, caller="command_line"):
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
    loaded_modules = state.loaded_modules
    opts = dict([(m.name, m.opts) for m in loaded_modules])
    for (i, other) in enumerate(loaded_modules):
        if other.name == module_a.name:
            # All modules coming after this one will be unloaded and
            # reloaded
            to_unload_and_reload = loaded_modules[i:]
            break
    else:  # pragma: no cover
        raise NoModulesToSwapError

    # Unload any that need to be unloaded first
    for other in to_unload_and_reload[::-1]:
        unload_impl(other, caller=caller)
    assert other.name == module_a.name

    # Now load it
    load_impl(module_b)

    # Reload any that need to be unloaded first
    for other in to_unload_and_reload[1:]:
        if maintain_state:
            this_module = modulecmd.modulepath.get(other.filename)
        else:
            this_module = modulecmd.modulepath.get(other.acquired_as)
        if this_module is None:
            # The only way this_module is None is if a swap of modules
            # caused a change to MODULEPATH making this module
            # unavailable.
            state.unloaded_on_mp_change(other)
            continue

        if this_module.filename != other.filename:
            state.swapped_on_mp_change(other, this_module)

        # Now load the thing
        this_module.opts = opts.get(this_module.name, this_module.opts)
        load_impl(this_module)

    return module_b


def unload(name, tolerant=False, caller="command_line"):
    """Unload the module given by `name`"""
    module = modulecmd.modulepath.get(name)
    if module is None:
        raise ModuleNotFoundError(name)

    for loaded in state.loaded_modules:
        if loaded.name == name:
            break
        elif loaded.fullname == name:
            break
    else:
        tty.warn("Module {0} is not loaded".format(name))
        return

    if modulecmd.environ.get(modulecmd.names.loaded_collection):  # pragma: no cover
        collection = modulecmd.environ.get(modulecmd.names.loaded_collection)
        tty.debug(
            "Unloading {0} on top of loaded collection {1}. "
            "Removing the collection name from the environment".format(
                module.fullname, collection
            )
        )
        modulecmd.environ.unset(modulecmd.names.loaded_collection)

    unload_impl(loaded, caller)
    return loaded


def unload_impl(module, caller="command_line"):
    """Implementation of unload

    Parameters
    ----------
    module : Module
        The module to unload
    """
    if not module.is_loaded:
        if caller == "command_line":
            raise ModuleNotLoadedError(module)
        return

    if module.refcount == 1 or caller == "command_line":
        execmodule(module, modulecmd.modes.unload)
        state.unregister_module(module)
    else:
        module.refcount -= 1

    module.reset_state()


def unuse(dirname):
    """Remove dirname from MODULEPATH"""

    dirname = os.path.expanduser(dirname)
    if not modulecmd.modulepath.contains(dirname):
        # Nothing to do!
        return

    # load them to initialize list of loaded modules
    _ = state.loaded_modules

    # Now remove dirname from MODULEPATH
    popped_modules = modulecmd.modulepath.remove_path(dirname)
    orphaned = determine_swaps_due_to_removal(popped_modules)

    # Unload orphans
    for orphan in orphaned[::-1]:
        unload_impl(orphan[0])

    # Load modules bumped by removal of dirname from MODULEPATH
    for orphan in orphaned:
        if orphan[1] is None:
            # No longer available!
            state.unloaded_on_mp_change(orphan[0])
        else:
            load_impl(orphan[1])
            state.swapped_on_mp_change(orphan[0], orphan[1])


def determine_swaps_due_to_removal(popped_modules):
    """Determine with of the popped modules should be swapped for modules that
    became available after removing a directory from the modulepath

    Parameters
    ----------
    popped_modules : list of Module
        Modules no longer available due to their modulepath being removed

    Return
    ------
    orphans : list of tuple
        orphans[i][0] loaded module left orphaned
        orphans[i][1] module to be loaded in its place, or None

    """

    # Determine which modules may have moved up in priority due to removal
    # of directory from path. If they have the same name as an orphan, it
    # will be loaded in the orphans place
    orphaned = [m for m in popped_modules if m.is_loaded]
    for (i, orphan) in enumerate(orphaned):
        for attr in ("fullname", "name"):
            other = modulecmd.modulepath.get(getattr(orphan, attr))
            if other is not None:
                orphaned[i] = (orphan, other)
                break
        else:
            orphaned[i] = (orphan, None)
    return orphaned


def use(dirname, append=False, delete=False):
    """Add dirname to MODULEPATH"""
    dirname = os.path.abspath(os.path.expanduser(dirname))
    if delete:
        unuse(dirname)
        return
    elif append:
        return modulecmd.modulepath.append_path(dirname)
    else:
        prepended_modules = modulecmd.modulepath.prepend_path(dirname)
        if prepended_modules is None:
            tty.warn(
                "No modules were found in {0}.  "
                "This path will not be added to MODULEPATH".format(dirname)
            )
            return None
        bumped = determine_swaps_due_to_prepend(prepended_modules)
        for (old, new) in bumped:
            assert old.is_loaded
            if new.fullname == old.acquired_as:
                new.acquired_as = old.acquired_as
            else:
                new.acquired_as = new.fullname
            swap_impl(old, new)
            state.swapped_on_mp_change(old, new)
        return bumped


def determine_swaps_due_to_prepend(prepended_modules):
    """Determine with modules lost precedence and need to be replaced

    Parameters
    ----------
    prepended_modules : list of Module
        These are modules that are now available from prepending their
        modulepath to modulecmd.modulepath

    Returns
    -------
    bumped : list of Module
        List of loaded modules that have lower precedence than a module of the
        same name in prepended_modules. These should be swapped

    """
    # Determine which modules changed in priority due to insertion of new
    # directory in to path
    bumped = []
    loaded_modules = state.loaded_modules

    # Check for fullname first
    fullnames = [m.fullname for m in prepended_modules]
    for (i, module) in enumerate(loaded_modules):
        if module.fullname not in fullnames:
            continue
        prepended_module = prepended_modules[fullnames.index(module.fullname)]
        if prepended_module.filename != module.filename:
            # The new module has the same name, but different filename. Since
            # new module has higher precedence (since its path was prepended to
            # modulepath), we swap them
            bumped.append((module, prepended_module))
            loaded_modules[i] = None

    names = [m.name for m in prepended_modules]
    for (i, module) in enumerate(loaded_modules):
        if module is None or module.name not in names:
            continue
        if module.acquired_as == module.fullname:  # pragma: no cover
            continue
        prepended_module = prepended_modules[names.index(module.name)]
        if prepended_module.filename != module.filename:
            bumped.append((module, prepended_modules[i]))

    return bumped


def trace(string):
    state.cur_module_command_his.write(string)


def whatis(name):
    """Display 'whatis' message for the module given by `name`"""
    module = modulecmd.modulepath.get(name)
    if module is None:
        raise ModuleNotFoundError(name, mp=modulecmd.modulepath)
    load_partial(module, mode=modulecmd.modes.whatis)
    return module.format_whatis()


class ModuleRegisteredError(Exception):
    def __init__(self, module):
        msg = "Attempting to register {0} which is already registered!"
        superini = super(ModuleRegisteredError, self).__init__
        superini(msg.format(module))


class ModuleNotRegisteredError(Exception):
    def __init__(self, module):
        msg = "Attempting to unregister {0} which is not registered!"
        superini = super(ModuleNotRegisteredError, self).__init__
        superini(msg.format(module))


class NoModulesToSwapError(Exception):
    pass
