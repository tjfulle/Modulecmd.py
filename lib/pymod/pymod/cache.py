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

    def get(self, modulepath):
        modules_cache = self.data.get(modulepath)
        if not modules_cache:
            return None
        modules = []
        for cached_module in modules_cache:
            module = pymod.module.from_dict(cached_module)
            if module is None:
                # A module was removed, this directory cache should be
                # invalidated so it can be rebuilt
                self.data[modulepath] = None
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

    def set(self, modulepath, modules):
        self.data[modulepath] = []
        for module in modules:
            self.data[modulepath].append(pymod.module.as_dict(module))
        self.dump()

    def remove(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)
        self.data = dict()

    def refresh(self):
        dirs = list(self.data.keys())
        self.data = dict()
        for dirname in dirs:
            find_modules(dirname)


_cache = Singleton(Cache)


def remove():
    _cache.remove()


def refresh():  # pragma: no cover
    _cache.refresh()


def put(modulepath, modules):
    _cache.set(modulepath, modules)


def get(modulepath):
    return _cache.get(modulepath)
