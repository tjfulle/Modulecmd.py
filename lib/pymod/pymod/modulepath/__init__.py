import os

import pymod.names
from contrib.util.misc import split
from contrib.util.lang import Singleton
from pymod.modulepath._modulepath import Modulepath


def _modulepath():
    path = split(os.getenv(pymod.names.modulepath), os.pathsep)
    return Modulepath(path)


mpath = Singleton(_modulepath)


def set_path(other_path):
    global mpath
    mpath = other_path


def group_by_modulepath(sort=False):
    return mpath.group_by_modulepath(sort=False)


def get(key):
    return mpath.get(key)


def append_path(dirname):
    return mpath.append_path(dirname)


def remove_path(dirname):
    return mpath.remove_path(dirname)


def prepend_path(dirname):
    return mpath.prepend_path(dirname)


def format_available(**kwargs):
    return mpath.format_available(**kwargs)


def candidates(name):
    return mpath.candidates(name)


def contains(path):
    return path in mpath
