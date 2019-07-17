import os
import json

import pymod.names
import pymod.modulepath

from llnl.util.lang import Singleton


cache_version_info = (0, 1, 0)


class Cache:
    def __init__(self, filename):
        self._modified = False
        self.filename = filename
        self.data = self.load()
        version = tuple(self.data.get('version', []))
        if self.data and version != cache_version_info:  # pragma: no cover
            # Old version, forget it
            self.data = {}
            self._modified = True
        self.data['version'] = cache_version_info

    @property
    def modified(self):
        return self._modified

    @modified.setter
    def modified(self, arg):
        self._modified = bool(arg)

    def get(self, section, key):
        if section == pymod.names.modulepath:
            return self._get_mp(key)

    def load(self):
        data = dict()
        if os.path.isfile(self.filename):
            try:
                data.update(dict(json.load(open(self.filename))))
            except json.decoder.JSONDecodeError:  # pragma: no cover
                self.remove()
        return data

    def write(self):
        with open(self.filename, 'w') as fh:
            json.dump(self.data, fh, indent=2)

    def set(self, section, key, item):
        if section == pymod.names.modulepath:
            return self._set_mp(key, item)

    def remove(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)
        self.data = dict()
        self.modified = True

    def _set_mp(self, dirname, modules):
        mp_data = self.data.setdefault(pymod.names.modulepath, {})
        mp_data[dirname] = [pymod.module.as_dict(m) for m in modules]
        self.modified = True

    def _get_mp(self, dirname):
        modules_cache = self.data.get(pymod.names.modulepath, {}).get(dirname)
        if modules_cache is None:
            return None
        modules = [pymod.module.from_dict(m) for m in modules_cache]
        if any([m is None for m in modules]):
            # A module was removed, this directory cache should be
            # invalidated so it can be rebuilt
            modules = None
            self.data[dirname] = modules
            self.modified = True
        return modules

    def build(self):
        """Build the cache"""
        self.data = {}
        self.data['version'] = cache_version_info

        # Build the modulepath cache
        for path in pymod.modulepath.walk():
            self._set_mp(path.path, path.modules)
        self.write()


def factory():
    basename = pymod.names.cache_file_basename
    filename = pymod.paths.join_user(basename)
    return Cache(filename)


cache = Singleton(factory)


def modified():
    return cache.modified


def set(section, key, item):
    cache.set(section, key, item)


def get(section, key):
    return cache.get(section, key)


def write():
    return cache.write()


def build():
    return cache.build()


def remove():
    cache.remove()
