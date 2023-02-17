import os
import json
import atexit

import modulecmd.names
import modulecmd.modulepath
import modulecmd.xio as xio
from modulecmd.util import singleton


cache_version_info = (0, 1, 0)


def modifies_cache(fun):
    from functools import wraps

    @wraps(fun)
    def inner(self, *args, **kwargs):
        returnvalue = fun(self, *args, **kwargs)
        self.modified = True
        return returnvalue

    return inner


class Cache:
    def __init__(self, filename):
        self._modified = False
        self.filename = filename
        self._data = None

    @property
    def data(self):
        if self._data is None:
            self._data = self.load()
            version = tuple(self._data.get("version", []))
            if self._data and version != cache_version_info:  # pragma: no cover
                # Old version, forget it
                self._data = {}
                self._modified = True
            self._data["version"] = cache_version_info
        return self._data

    @property
    def modified(self):
        return self._modified

    @modified.setter
    def modified(self, arg):
        self._modified = bool(arg)

    def load(self):
        data = dict()
        if os.path.isfile(self.filename):
            try:
                data.update(dict(json.load(open(self.filename))))
            except json.decoder.JSONDecodeError:  # pragma: no cover
                self.remove()
        return data

    def write(self):
        with open(self.filename, "w") as fh:
            json.dump(self.data, fh, indent=2)

    @modifies_cache
    def remove(self):
        xio.info("Removing the MODULEPATH cache")
        if os.path.isfile(self.filename):
            os.remove(self.filename)
        self._data = dict()

    def get(self, section, key, default=None):
        return self.data.setdefault(section, {}).get(key, default)

    @modifies_cache
    def pop(self, section, key, default=None):
        section_data = self.data.setdefault(section, {})
        items = section_data.pop(key, default)
        return items

    @modifies_cache
    def set(self, section, key, item):
        section_data = self.data.setdefault(section, {})
        section_data[key] = item

    def build(self):
        """Build the cache"""
        xio.info("Building the MODULEPATH cache")
        self._data = {}
        self._data["version"] = cache_version_info

        # Build the modulepath cache
        for path in modulecmd.modulepath.path():
            modulecmd.modulepath.find_modules(path)
        self.write()


def factory():
    basename = modulecmd.names.cache_file_basename
    filename = modulecmd.paths.join_user(basename, cache=True)
    return Cache(filename)


cache = singleton(factory)


def modified():
    return cache.modified


def set(section, key, item):
    cache.set(section, key, item)


def get(section, key):
    return cache.get(section, key)


def pop(section, key):
    return cache.pop(section, key)


def write():
    return cache.write()


def build():
    return cache.build()


def remove():
    cache.remove()


def dump_cache_if_modified():  # pragma: no cover
    if cache.modified:
        cache.write()


atexit.register(dump_cache_if_modified)
