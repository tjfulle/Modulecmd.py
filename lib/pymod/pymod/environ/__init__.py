import os

from contrib.util import join, split, dict2str, str2dict
from pymod.environ._environ import Environ
from llnl.util.lang import Singleton


environ = Singleton(Environ)


def reset():
    global environ
    environ = Environ()


def format_output():
    return environ.format_output()


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
    return split(environ.get(key), sep=sep)


def set_path(key, path, sep=os.pathsep):
    value = join(path, sep=sep)
    return environ.set(key, value)


def get_dict(key):
    return str2dict(environ.get(key))


def set_dict(key, dict):
    value = dict2str(dict)
    return environ.set(key, value)
