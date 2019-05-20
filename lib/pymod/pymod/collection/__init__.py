import os
import pymod.paths
import pymod.config
from llnl.util.lang import Singleton
from pymod.collection._collection import Collections


def _collections():
    basename = pymod.names.collections_file_basename
    for dirname in (pymod.paths.user_config_platform_path,
                    pymod.paths.user_config_path):
        filename = os.path.join(dirname, basename)
        if os.path.exists(filename):  # pragma: no cover
            break
        # it is okay that we may not have found a config file, if it doesn't
        # exist, Collections will create it
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
