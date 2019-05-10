import os
from argparse import Namespace

import pymod.names
import pymod.shell
import pymod.modulepath
from contrib.util import str2dict, dict2str, boolean, split, join, pop

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
        p.meta = str2dict(self.get(p.meta_key))
        return p

    def set_path(self, path):
        if not path.value:
            self[path.key] = None
            self[path.meta_key] = None
        else:
            self[path.key] = join(path.value, path.sep)
            self[path.meta_key] = dict2str(path.meta)
        self.save_ld_library_path(path.key)

    def filtered(self, include_os=True):
        env = dict() if not include_os else dict(os.environ)
        env.update(dict([item for item in self.items() if item[1] is not None]))
        env.update(pymod.modulepath.export_env())
        pymod_env = dict()
        for (key, val) in env.items():
            if pymod.shell.filter_key(key):
                continue
            pymod_env[key] = val
        return pymod_env

    def copy(self, include_os=True):
        env = dict() if not include_os else dict(os.environ)
        env.update(self)
        env.update(pymod.modulepath.export_env())
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
            self['__{}__'.format(key)] = self[key]

    def set(self, key, value):
        key = self.fix_ld_library_path(key)
        self[key] = value
        self.save_ld_library_path(key)

    def unset(self, key):
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
                'Do not set MODULEPATH directly in Environ object.  '
                'Set it in the Modulepath instead')
        key = self.fix_ld_library_path(key)
        allow_dups = self.get_bool(pymod.names.allow_dup_entries)
        current_path = self.get_path(key, sep=sep)
        count, priority = current_path.meta.pop(value, (0, -1))
        if count == 0 and value in current_path.value:
            count = current_path.value.count(value)
        count -= 1
        if (allow_dups and count > 0) or count <= 0:
            pop(current_path.value, value)
        if count > 0:
            current_path.meta[value] = (count, priority)
        self.set_path(current_path)
