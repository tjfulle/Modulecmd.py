import os

import pymod.names
from pymod.modulepath.modulepath import Modulepath
from pymod.modulepath.discover import find_modules

from pymod.util.lang import split
from llnl.util.lang import Singleton


def factory():  # pragma: no cover
    path = split(os.getenv(pymod.names.modulepath), os.pathsep)
    return Modulepath(path)


_path = Singleton(factory)


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


def avail(**kwargs):
    return _path.avail(**kwargs)


def candidates(name):
    return _path.candidates(name)


def contains(path):
    return path in _path


def walk(start=0):
    return _path.walk(start=0)


def size():
    return _path.size()


def clear():
    return _path.clear()
