import os
from argparse import Namespace

import pymod.names
import pymod.shell
import pymod.modulepath

from contrib.util import boolean
from contrib.util import join, split, pop
from pymod.serialize import serialize, deserialize
from pymod.serialize import serialize_to_dict, deserialize_from_dict

import llnl.util.tty as tty
from llnl.util.lang import Singleton


class Environ(dict):

    def __init__(self):
        self.aliases = {}
        self.shell_functions = {}

    def is_empty(self):
        return (not len(self) and
                not len(self.aliases) and
                not len(self.shell_functions))

    def format_output(self):
        env = self.copy()
        return pymod.shell.format_output(
            env, self.aliases, self.shell_functions)

    def get(self, key, default=None):
        if key in self:
            return self[key]
        elif key in os.environ:
            return os.environ[key]
        return default

    def get_bool(self, key):
        return boolean(self.get(key))

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
        p.meta_key = pymod.names.loaded_module_meta(key)
        p.sep = sep
        p.value = split(self.get(key), sep=sep)
        meta = self.get(p.meta_key)
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

    def copy(self, include_os=False, filter_None=False):
        env = dict(os.environ) if include_os else dict()
        if filter_None:
            env.update(dict([item for item in self.items() if item[1] is not None]))
        else:
            env.update(self)

        # Modulepath is a special case
        mp = pymod.modulepath._path.value
        if include_os:
            env[pymod.names.modulepath] = mp
        elif mp != os.getenv(pymod.names.modulepath):
            env[pymod.names.modulepath] = mp

        pymod_env = dict()
        for (key, val) in env.items():
            if pymod.shell.filter_key(key):
                continue
            pymod_env[key] = val

        return pymod_env

    @staticmethod
    def fix_ld_library_path(key):
        if key.endswith(pymod.names.ld_library_path):
            key = pymod.names.ld_library_path
        return key

    def save_ld_library_path(self, key):
        if key.endswith(pymod.names.ld_library_path):
            # sometimes python doesn't pick up ld_library_path :(
            self['__{0}__'.format(key)] = self[key]

    def set(self, key, value):
        if key == pymod.names.modulepath:
            raise ValueError(
                'Do not set MODULEPATH directly in Environ object.  '
                'Set it in the Modulepath instead')
        key = self.fix_ld_library_path(key)
        self[key] = value
        self.save_ld_library_path(key)

    def unset(self, key):
        if key == pymod.names.modulepath:
            raise ValueError(
                'Do not set MODULEPATH directly in Environ object.  '
                'Unset it in the Modulepath instead')
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
        if key == pymod.names.modulepath:
            raise ValueError(
                'Do not set MODULEPATH directly in Environ object.  '
                'Set it in the Modulepath instead')
        key = self.fix_ld_library_path(key)
        allow_dups = self.get_bool(pymod.names.allow_dup_entries)
        current_path = self.get_path(key, sep=sep)
        count, priority = current_path.meta.pop(value, (0, -1))
        if count == 0 and value in current_path.value:
            count = current_path.value.count(value)
        count += 1
        if allow_dups or value not in current_path.value:
            current_path.value.append(value)
        current_path.meta[value] = (count, priority)
        self.set_path(current_path)

    def prepend_path(self, key, value, sep=os.pathsep):
        if key == pymod.names.modulepath:
            raise ValueError(
                'Do not set MODULEPATH directly in Environ object.  '
                'Set it in the Modulepath instead')
        key = self.fix_ld_library_path(key)
        allow_dups = self.get_bool(pymod.names.allow_dup_entries)
        current_path = self.get_path(key, sep=sep)
        count, priority = current_path.meta.pop(value, (0, -1))
        if count == 0 and value in current_path.value:
            count = current_path.value.count(value)
        count += 1
        if not allow_dups:
            pop(current_path.value, value)
        current_path.value.insert(0, value)
        current_path.meta[value] = (count, priority)
        self.set_path(current_path)

    def remove_path(self, key, value, sep=os.pathsep):
        if key == pymod.names.modulepath:
            raise ValueError(
                'Do not remove MODULEPATH directly from Environ object.  '
                'Use the Modulepath object instead')
        key = self.fix_ld_library_path(key)
        allow_dups = self.get_bool(pymod.names.allow_dup_entries)
        current_path = self.get_path(key, sep=sep)
        count, priority = current_path.meta.pop(value, (0, -1))
        if count == 0 and value in current_path.value: # pragma: no cover
            tty.warn('Inconsistent refcount state')
            count = current_path.value.count(value)
            if pymod.config.get('debug'):
                raise Exception('Inconsistent refcount state')
        count -= 1
        if (allow_dups and count > 0) or count <= 0:
            pop(current_path.value, value)
        if count > 0:
            current_path.meta[value] = (count, priority)
        self.set_path(current_path)


environ = Singleton(Environ)


def set_env(env):
    global environ
    environ = env


def is_empty():
    return environ.is_empty()


def format_output():
    return environ.format_output()


def get(key, default=None):
    return environ.get(key, default)


def get_bool(key):
    return environ.get_bool(key)


def set(key, value):
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


def serialize_and_set(key, arg, _type):
    value = serialize(arg or _type())
    return environ.set(key, value)


def get_and_deserialize(key, _type):
    serialized = environ.get(key)
    return _type() if serialized is None else deserialize(serialized)


def get_dict(key):
    return get_and_deserialize(key, dict)


def set_dict(key, arg):
    serialize_and_set(key, arg, dict)


def get_list(key):
    return get_and_deserialize(key, list)


def set_list(key, arg):
    serialize_and_set(key, arg, list)


def filtered(include_os=False):
    return environ.filtered(include_os=include_os)


def copy(include_os=False):
    return environ.copy(include_os=include_os)


def get_lm_cellar(env=None):
    return deserialize_from_dict(environ, pymod.names.loaded_module_cellar)


def set_lm_cellar(cellar):
    serialized = serialize_to_dict(cellar, pymod.names.loaded_module_cellar)
    for (key, chunk) in serialized.items():
        environ.set(key, chunk)
