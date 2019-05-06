import os

from pymod.environ._environ import Environ
from contrib.util.lang import Singleton


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
