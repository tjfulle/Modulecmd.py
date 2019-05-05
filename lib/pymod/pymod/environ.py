import os
from argparse import Namespace

import pymod.names
from contrib.util.lang import Singleton
from contrib.util.misc import str2dict, dict2str, boolean, split, join, pop
from contrib.ordereddict_backport import OrderedDict

class Environ(OrderedDict):

    def __init__(self):
        self.aliases = {}
        self.shell_functions = {}

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
        p.key = key
        p.meta_key = pymod.names.loaded_module_meta(key)
        p.sep = sep
        p.value = split(self.get(key), sep=sep)
        p.meta = str2dict(self.get(p.meta_key))
        return p

    def set(self, key, value):
        self[key] = value

    def unset(self, key):
        self[key] = None

    def set_alias(self, key, value):
        self.aliases[key] = value

    def unset_alias(self, key):
        self.aliases[key] = None

    def set_shell_function(self, key, value):
        self.shell_functions[key] = value

    def unset_shell_function(self, key):
        self.shell_functions[key] = None

    def set_path(self, path):
        if not path.value:
            self[path.key] = None
            self[path.meta_key] = None
        else:
            self[path.key] = join(path.value, path.sep)
            self[path.meta_key] = dict2str(path.meta)

    def append_path(self, key, value, sep=os.pathsep):
        if key == pymod.names.modulepath:
            raise NotImplemented
        allow_dups = self.get_bool('PYMOD_ALLOW_DUPLICATE_PATH_ENTRIES')
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
            raise NotImplemented
        allow_dups = self.get_bool('PYMOD_ALLOW_DUPLICATE_PATH_ENTRIES')
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
        allow_dups = self.get_bool('PYMOD_ALLOW_DUPLICATE_PATH_ENTRIES')
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


environ = Singleton(Environ)

def reset():
    global environ
    environ = Environ()


def get(key, default=None):
    return environ.get(key, default)

def get_bool(key):
    return eniron.get_bool(key)

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
    path = environ.get_path(key, sep=sep)
    return path.value
