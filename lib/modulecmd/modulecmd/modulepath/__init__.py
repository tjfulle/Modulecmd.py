import os

import modulecmd.names
from modulecmd.modulepath.path import Path
from modulecmd.modulepath.modulepath import Modulepath
from modulecmd.modulepath.discover import find_modules

from modulecmd.util.lang import split
from llnl.util.lang import Singleton


def factory():  # pragma: no cover
    path = split(os.getenv(modulecmd.names.modulepath), os.pathsep)
    return Modulepath(path)


_path = Singleton(factory)


def path():
    return list(_path.path.keys())


def set_path(other_path):
    global _path
    _path = other_path


def get(key, use_file_modulepath=False):
    return _path.get(key, use_file_modulepath=use_file_modulepath)


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


def size():
    return _path.size()


def clear():
    return _path.clear()
