import os
from string import Template
import modulecmd.cache
import modulecmd.names
import modulecmd.config
import modulecmd.module
from modulecmd.modulepath.discover import find_modules


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
        if not modulecmd.config.get("use_modulepath_cache"):  # pragma: no cover
            return None
        key = self.path
        section = modulecmd.names.modulepath
        cached = modulecmd.cache.get(section, key)
        if cached is None:
            return None

        modules = [modulecmd.module.from_dict(m) for m in cached]
        if any([m is None for m in modules]):
            # A module was removed, the cache is invalid
            modulecmd.cache.pop(section, key)
            return None
        return modules

    def cache_modules(self, modules):
        if not modulecmd.config.get("use_modulepath_cache"):  # pragma: no cover
            return
        key = self.path
        section = modulecmd.names.modulepath
        data = [modulecmd.module.as_dict(m) for m in modules]
        modulecmd.cache.set(section, key, data)

    @classmethod
    def expand_name(cls, dirname):
        return os.path.expanduser(Template(dirname).safe_substitute(**(os.environ)))
