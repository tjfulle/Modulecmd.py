import os
from string import Template
import pymod.cache
import pymod.names
import pymod.config
import pymod.module
from pymod.modulepath.discover import find_modules


class Path:
    """Class to hold modules in a directory"""

    def __init__(self, dirname):
        self.path = self.expand_name(dirname)
        self.modules = self.find_modules()

    def find_modules(self):
        cached_modules = self.get_cached_modules()
        if cached_modules is not None:
            return cached_modules
        else:
            modules = find_modules(self.path)
            if modules:
                self.cache_modules(modules)
            return modules

    def get_cached_modules(self):
        if not pymod.config.get("use_modulepath_cache"):  # pragma: no cover
            return None
        key = self.path
        section = pymod.names.modulepath
        cached = pymod.cache.get(section, key)
        if cached is None:
            return None

        modules = [pymod.module.from_dict(m) for m in cached]
        if any([m is None for m in modules]):
            # A module was removed, the cache is invalid
            pymod.cache.pop(section, key)
            return None
        return modules

    def cache_modules(self, modules):
        if not pymod.config.get("use_modulepath_cache"):  # pragma: no cover
            return
        key = self.path
        section = pymod.names.modulepath
        data = [pymod.module.as_dict(m) for m in modules]
        pymod.cache.set(section, key, data)

    @classmethod
    def expand_name(cls, dirname):
        return os.path.expanduser(Template(dirname).safe_substitute(**(os.environ)))
