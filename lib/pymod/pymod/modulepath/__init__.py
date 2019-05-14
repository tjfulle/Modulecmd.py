import os

import pymod.names
from contrib.util import split
from llnl.util.lang import Singleton
from pymod.modulepath._modulepath import Modulepath, Path


def _modulepath():
    path = split(os.getenv(pymod.names.modulepath), os.pathsep)
    return Modulepath(path)


_path = Singleton(_modulepath)


def export_env():
    return _path.export_env()


def path():
    return [p.path for p in _path.path]


def set_path(other_path):
    global _path
    _path = other_path


def get(key):
    return _path.get(key)


def append_path(dirname):
    return _path.append_path(dirname)


def remove_path(dirname):
    return _path.remove_path(dirname)


def prepend_path(dirname):
    return _path.prepend_path(dirname)


def format_available(**kwargs):
    return _path.format_available(**kwargs)


def candidates(name):
    return _path.candidates(name)


def contains(path):
    return path in _path


def size():
    return len(_path)


def clear():
    _path.clear()
