import os
import pymod.names
import pymod.paths
from llnl.util.lang import Singleton
from pymod.collection._collection import Collections


def _collections():
    basename = pymod.names.collections_file_basename
    for dirname in (pymod.paths.user_config_platform_path,
                    pymod.paths.user_config_path):
        filename = os.path.join(dirname, basename)
        if os.path.exists(filename):  # pragma: no cover
            break
    else:
        filename = os.path.join(
            pymod.paths.user_config_platform_path,
            basename)

    # it is okay that we may not have found a config file, if it doesn't
    # exist, Collections will create it
    return Collections(filename)


collections = Singleton(_collections)


def save(name, loaded_modules):
    return collections.save(name, loaded_modules)


def remove(name):
    return collections.remove(name)


def get(name):
    return collections.get(name)


def avail(terse=False, regex=None):
    return collections.avail(terse=terse, regex=regex)


def show(name):
    return collections.show(name)


def is_collection(name):
    return name in collections


def contains(name):
    return is_collection(name)


def version():
    return Collections.version
