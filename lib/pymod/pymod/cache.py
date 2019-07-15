import os
import json

import pymod.names
from pymod.modulepath.discover import find_modules

from llnl.util.lang import Singleton


class Cache:
    def __init__(self, filename=None):
        if filename is None:
            basename = pymod.names.cache_file_basename
            for dirname in (pymod.paths.user_config_platform_path,
                            pymod.paths.user_config_path):
                filename = os.path.join(dirname, basename)
                if os.path.exists(filename):  # pragma: no cover
                    break
            else:
                filename = os.path.join(
                    pymod.paths.user_config_platform_path,
                    basename)
        self.filename = filename
        self.data = self.load()
        self._modified = False

    @property
    def modified(self):
        return self._modified

    def get(self, dirname):
        modules_cache = self.data.get(dirname)
        if not modules_cache:
            return None
        modules = []
        for cached_module in modules_cache:
            module = pymod.module.from_dict(cached_module)
            if module is None:
                # A module was removed, this directory cache should be
                # invalidated so it can be rebuilt
                self.data[dirname] = None
                return
            modules.append(module)
        return modules

    def load(self):
        data = dict()
        if os.path.isfile(self.filename):
            data.update(dict(json.load(open(self.filename))))
        return data

    def dump(self):
        with open(self.filename, 'w') as fh:
            json.dump(self.data, fh, indent=2)

    def set(self, dirname, modules):
        self.data[dirname] = []
        for module in modules:
            self.data[dirname].append(pymod.module.as_dict(module))
        self._modified = True
        #self.dump()

    def remove(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)
        self.data = dict()
        self._modified = True

    def refresh(self):
        dirs = list(self.data.keys())
        self.data = dict()
        for dirname in dirs:
            find_modules(dirname)
        self._modified = True


_cache = Singleton(Cache)


def modified():  # pragma: no cover
    if isinstance(_cache, Singleton):
        return False
    return _cache.modified


def remove():
    _cache.remove()


def refresh():  # pragma: no cover
    _cache.refresh()


def put(dirname, modules):
    _cache.set(dirname, modules)


def get(dirname):
    return _cache.get(dirname)
