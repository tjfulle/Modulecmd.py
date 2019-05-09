import os
import pymod.paths
import pymod.config
from llnl.util.lang import Singleton
from pymod.collection._collection import Collections
import llnl.util.tty as tty


def _collections():
    filename = os.path.join(
        pymod.paths.user_config_path,
        pymod.config.get('collections_filename'))
    return Collections(filename)


collections = Singleton(_collections)


def save(name, loaded_modules, local=False):
    return collections.save(name, loaded_modules, local)


def remove(name):
    return collections.remove(name)


def get(name):
    return collections.get(name)


def format_available(terse=False, regex=None):
    return collections.format_available(terse=terse, regex=regex)


def format_show(name):
    return collections.format_show(name)


def is_collection(name):
    return name in collections


def contains(name):
    return is_collection(name)
