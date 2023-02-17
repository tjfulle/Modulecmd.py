import os
from configparser import ConfigParser

from modulecmd.util import singleton, split, which


has_tclsh = which("tclsh") is not None


default_settings = {
    "debug": False,
    "verbose": False,
    "default_shell": "bash",
    "warn_all": True,
    "stop_on_error": True,
    "resolve_conflicts": False,
    "allow_duplicate_path_entries": False,
    "editor": "vi",
    "load_after_purge": [],
    "skip_add_devpack": False,
    "color": "auto",
    "serialize_chunk_size": -1,
    "compress_serialized_variables": True,
    "use_modulepath_cache": True,
    "tclsh": has_tclsh,
}


class configuration:
    def __init__(self):
        config_dir = os.getenv("MODULECMD_CONFIG_DIR", "~")
        self.config_dir = os.path.expanduser(config_dir)
        self.config_file = os.path.join(self.config_dir, ".modulecmd.ini")
        self.data = dict(default_settings)
        if os.path.exists(self.config_file):
            fd = ConfigParser()
            fd.read(self.config_file)
            for (key, default_value) in self.data.items():
                if not fd.has_option("modulecmd", key):
                    continue
                elif isinstance(default_value, bool):
                    value = fd.getboolean("modulecmd", key)
                elif isinstance(default_value, int):
                    value = fd.getint("modulecmd", key)
                elif isinstance(default_value, float):
                    value = fd.getfloat("modulecmd", key)
                elif isinstance(default_value, list):
                    value = split(fd.get("modulecmd", key), sep=None)
                else:
                    value = fd.get("modulecmd", key)
                self.data[key] = value

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value


_config = singleton(configuration)


def get(key, default=None, scope=None):
    """Module-level wrapper for ``Configuration.get()``."""
    return _config.get(key, default=default)


def set(key, value, scope=None):  # pragma: no cover
    """Convenience function for getting single values in config files."""
    return _config.set(key, value)


def config_file():
    return _config.config_file
