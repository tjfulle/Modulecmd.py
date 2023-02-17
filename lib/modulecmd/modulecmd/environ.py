import os
import sys
from argparse import Namespace

import modulecmd.names
import modulecmd.shell
import modulecmd.modulepath

from modulecmd.serialize import serialize, deserialize
from modulecmd.serialize import serialize_chunked, deserialize_chunked
from modulecmd.util.lang import join, split, pop, get_system_manpath

import llnl.util.tty as tty
from llnl.util.lang import Singleton


class Environ(dict):
    def __init__(self):
        self.aliases = {}
        self.shell_functions = {}
        self.destination_dir = None
        self._sys_manpath = None
        self.files_to_source = []
        self.raw_shell_commands = []

    def __getitem__(self, key):
        """Overload Environ[] to first check me, then os.environ"""
        if key in self:
            return super(Environ, self).__getitem__(key)
        return os.environ[key]

    def is_empty(self):
        return not len(self) and not len(self.aliases) and not len(self.shell_functions)

    def format_output(self):
        env = self.copy()
        output = modulecmd.shell.format_output(
            env,
            aliases=self.aliases,
            shell_functions=self.shell_functions,
            files_to_source=self.files_to_source,
            raw_shell_commands=self.raw_shell_commands,
        )
        if self.destination_dir is not None:
            output += "cd {0};".format(self.destination_dir)
        return output

    def set_destination_dir(self, dirname):
        if not os.path.isdir(dirname):
            tty.die("{0} is not a directory".format(dirname))
        self.destination_dir = dirname

    def get(self, key, default=None, type=None):
        """Overload Environ.get to first check me, then os.environ"""
        val = super(Environ, self).get(key, os.getenv(key, default))
        return val if type is None else type(val)

    def get_path(self, key, sep=os.pathsep):
        """Get the path given by `key`

        When paths are saved, the path value is saved and also some meta data.
        Currently, the saved meta data are the reference count and priority,
        though priority is not yet used.

        The meta data are saved in a dictionary in the environment variable
        `loaded_module_meta(key)`

        """
        p = Namespace()
        p.key = self.fix_ld_library_path(key)
        p.meta_key = modulecmd.names.loaded_module_meta(key)
        p.sep = sep
        p.value = split(self.get(key), sep=sep)
        serialized = self.get(p.meta_key)
        p.meta = {} if serialized is None else deserialize(serialized)
        return p

    def set_path(self, path):
        if not path.value:
            self[path.key] = None
            self[path.meta_key] = None
        else:
            self[path.key] = join(path.value, path.sep)
            self[path.meta_key] = serialize(path.meta)
        self.save_ld_library_path(path.key)

    def filtered(self, include_os=False):
        return self.copy(include_os=include_os, filter_None=True)

    def clone(self):
        return {
            "aliases": self.aliases.copy(),
            "shell_functions": self.shell_functions.copy(),
            "env": self.copy(),
        }

    def restore(self, clone):
        self.aliases = clone["aliases"]
        self.shell_functions = clone["shell_functions"]
        for key in list(self.keys()):
            del self[key]
        self.update(clone["env"])

    def copy(self, include_os=False, filter_None=False):
        env = dict(os.environ) if include_os else dict()
        if filter_None:
            env.update(dict([item for item in self.items() if item[1] is not None]))
        else:
            env.update(self)

        # Modulepath is a special case
        mp = modulecmd.modulepath._path.value
        if include_os:
            env[modulecmd.names.modulepath] = mp
        elif mp != os.getenv(modulecmd.names.modulepath):
            env[modulecmd.names.modulepath] = mp

        modulecmd_env = dict()
        for (key, val) in env.items():
            if modulecmd.shell.filter_key(key):
                continue
            modulecmd_env[key] = val

        return modulecmd_env

    @staticmethod
    def fix_ld_library_path(key):
        if key == modulecmd.names.ld_library_path:
            key = modulecmd.names.platform_ld_library_path
        return key

    @property
    def sys_manpath(self):  # pragma: no cover
        if self._sys_manpath is None:
            self._sys_manpath = get_system_manpath()
        return self._sys_manpath

    def set_manpath_if_needed(self):  # pragma: no cover
        if sys.platform == "darwin" and not self.get(modulecmd.names.manpath):
            # On macOS, MANPATH, if set, must also include system paths,
            # otherwise man will not search the system paths (it only searches
            # MANPATH)
            self.set(modulecmd.names.manpath, self.sys_manpath)

    def unset_manpath_if_needed(self, path):  # pragma: no cover
        assert path.key == modulecmd.names.manpath
        if sys.platform == "darwin":
            cur_manpath = join(path.value, sep=os.pathsep)
            if cur_manpath == self.sys_manpath:
                path.value = None

    def save_ld_library_path(self, key):
        if key.endswith(modulecmd.names.ld_library_path):
            # sometimes python doesn't pick up ld_library_path :(
            self["__{0}__".format(key)] = self[key]

    def set(self, key, value):
        if key == modulecmd.names.modulepath:
            raise ValueError(
                "Do not set MODULEPATH directly in Environ object.  "
                "Set it in the Modulepath instead"
            )
        key = self.fix_ld_library_path(key)
        self[key] = value
        self.save_ld_library_path(key)

    def unset(self, key):
        if key == modulecmd.names.modulepath:
            raise ValueError(
                "Do not set MODULEPATH directly in Environ object.  "
                "Unset it in the Modulepath instead"
            )
        key = self.fix_ld_library_path(key)
        self[key] = None
        self.save_ld_library_path(key)

    def set_alias(self, key, value):
        self.aliases[key] = value

    def unset_alias(self, key):
        self.aliases[key] = None

    def set_shell_function(self, key, value):
        self.shell_functions[key] = value

    def unset_shell_function(self, key):
        self.shell_functions[key] = None

    def append_path(self, key, value, sep=os.pathsep):
        if key == modulecmd.names.manpath:  # pragma: no cover
            self.set_manpath_if_needed()
        elif key == modulecmd.names.modulepath:
            raise ValueError(
                "Do not set MODULEPATH directly in Environ object.  "
                "Set it in the Modulepath instead"
            )
        key = self.fix_ld_library_path(key)
        allow_dups = modulecmd.config.get("allow_duplicate_path_entries")
        current_path = self.get_path(key, sep=sep)
        d = current_path.meta.pop(value, {"count": 0, "priority": -1})
        if d["count"] == 0 and value in current_path.value:
            d["count"] = current_path.value.count(value)
        d["count"] += 1
        if allow_dups or value not in current_path.value:
            current_path.value.append(value)
        current_path.meta[value] = d
        self.set_path(current_path)

    def prepend_path(self, key, value, sep=os.pathsep):
        if key == modulecmd.names.manpath:  # pragma: no cover
            self.set_manpath_if_needed()
        elif key == modulecmd.names.modulepath:
            raise ValueError(
                "Do not set MODULEPATH directly in Environ object.  "
                "Set it in the Modulepath instead"
            )
        key = self.fix_ld_library_path(key)
        allow_dups = modulecmd.config.get("allow_duplicate_path_entries")
        current_path = self.get_path(key, sep=sep)
        d = current_path.meta.pop(value, {"count": 0, "priority": -1})
        if d["count"] == 0 and value in current_path.value:
            d["count"] = current_path.value.count(value)
        d["count"] += 1
        if not allow_dups:
            pop(current_path.value, value)
        current_path.value.insert(0, value)
        current_path.meta[value] = d
        self.set_path(current_path)

    def remove_path(self, key, value, sep=os.pathsep):
        if key == modulecmd.names.modulepath:
            raise ValueError(
                "Do not remove MODULEPATH directly from Environ object.  "
                "Use the Modulepath object instead"
            )
        key = self.fix_ld_library_path(key)
        allow_dups = modulecmd.config.get("allow_duplicate_path_entries")
        current_path = self.get_path(key, sep=sep)
        d = current_path.meta.pop(value, {"count": 0, "priority": -1})
        if d["count"] == 0 and value in current_path.value:  # pragma: no cover
            tty.warn("Inconsistent refcount state")
            d["count"] = current_path.value.count(value)
            if modulecmd.config.get("debug"):
                raise Exception("Inconsistent refcount state")
        d["count"] -= 1
        if (allow_dups and d["count"] > 0) or d["count"] <= 0:
            pop(current_path.value, value)
        if d["count"] > 0:
            current_path.meta[value] = d
        if key == modulecmd.names.manpath:  # pragma: no cover
            self.unset_manpath_if_needed(current_path)
        self.set_path(current_path)

    def source_file(self, filename, *args):
        self.files_to_source.append((filename, args))

    def raw_shell_command(self, command):
        self.raw_shell_commands.append(command)


def factory():
    return Environ()


environ = Singleton(factory)


def set_env(env):
    global environ
    environ = env


def is_empty():
    return environ.is_empty()


def format_output():
    return environ.format_output()


def get(key, default=None, serialized=False, type=None):
    if serialized:
        return _get_and_deserialize(environ, key, default=default)
    return environ.get(key, default, type=type)


def set(key, value, serialize=False):
    if serialize:
        return _serialize_and_set(environ, key, value)
    return environ.set(key, value)


def unset(key):
    return environ.unset(key)


def set_alias(key, value):
    return environ.set_alias(key, value)


def unset_alias(key):
    return environ.unset_alias(key)


def set_shell_function(key, value):
    return environ.set_shell_function(key, value)


def unset_shell_function(key):
    return environ.unset_shell_function(key)


def append_path(key, value, sep=os.pathsep):
    return environ.append_path(key, value, sep)


def prepend_path(key, value, sep=os.pathsep):
    return environ.prepend_path(key, value, sep)


def remove_path(key, value, sep=os.pathsep):
    return environ.remove_path(key, value, sep)


def get_path(key, sep=os.pathsep):
    return split(environ.get(key), sep=sep)


def set_path(key, path, sep=os.pathsep):
    value = join(path, sep=sep)
    return environ.set(key, value)


def _serialize_and_set(container, label, value):

    # Reset previously set values
    for (key, item) in os.environ.items():
        if key.startswith(label):
            container.set(key, None)

    # Serialize the
    if value is None:
        key = modulecmd.names.serialized_key(label, 0)
        container.set(key, None)
        return

    serialized = serialize_chunked(value)
    for (i, chunk) in enumerate(serialized):
        key = modulecmd.names.serialized_key(label, i)
        container.set(key, chunk)


def _get_and_deserialize(container, label, default=None):
    i = 0
    chunks = []
    while True:
        key = modulecmd.names.serialized_key(label, i)
        try:
            chunk = container[key]
        except KeyError:
            break
        if chunk is None:
            return None
        chunks.append(chunk)
        i += 1
    if not chunks:
        return default
    return deserialize_chunked(chunks)


def filtered(include_os=False):
    return environ.filtered(include_os=include_os)


def copy(include_os=False):
    return environ.copy(include_os=include_os)


def clone():
    return environ.clone()


def restore(the_clone):
    return environ.restore(the_clone)


def set_destination_dir(dirname):
    environ.set_destination_dir(dirname)


def source_file(filename, *args):
    environ.source_file(filename, *args)


def raw_shell_command(command):
    environ.raw_shell_command(command)
