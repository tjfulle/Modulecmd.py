import os
import sys
import contrib.ruamel.yaml as yaml
import pymod.paths
from contrib.util.lang import Singleton


def load_yaml(filename, section=None):
    dict = yaml.load(open(filename))
    if section is not None:
        return dict.get(section)
    return dict


class Configuration(object):
    scope_names = ['defaults', 'user', 'environment', 'command_line']
    def __init__(self):
        self.scopes = {}

    def push_scope(self, scope_name, data):
        """Add a scope to the Configuration."""
        self.scopes.setdefault(scope_name, {}).update(dict(data))

    def remove_scope(self, scope_name):
        return self.scopes.pop(scope_name)

    def get(self, key, default=None, scope=None):
        if key is None:
            if scope is not None:
                return self.scopes[scope]
            cfg = {}
            for scope_name in self.scope_names[::-1]:
                if scope_name in self.scopes:
                    cfg.update(self.scopes[scope_name])
            return cfg

        if scope is not None:
            value = self.scopes[scope].get(key, default)
        else:
            for scope_name in self.scope_names[::-1]:
                if scope_name in self.scopes:
                    value = self.scopes[scope_name].get(key)
                    if value is not None:
                        break
            else:
                value = default
        return value

    def set(self, key, value, scope=None):
        if scope is not None:
            self.scopes.setdefault(scope, {}).update({key: value})
        else:
            for scope_name in self.scope_names[::-1]:
                self.scopes.setdefault(scope_name, {}).update({key: value})

def _config():
    """Singleton Configuration instance.

    This constructs one instance associated with this module and returns
    it. It is bundled inside a function so that configuratoin can be
    initialized lazily.

    Returns
    -------
    cfg : Configuration
        object for accessing spack configuration

    """
    cfg = Configuration()

    f = 'config.yaml'
    default_config_file = os.path.join(pymod.paths.etc_path, f)
    defaults = load_yaml(default_config_file, 'config')
    cfg.push_scope('defaults', defaults)

    test_in_progress = getattr(sys, '_pytest_in_progress_', False)
    if not test_in_progress:
        user_config_file = os.getenv(
            pymod.names.config_file_envar,
            os.path.join(pymod.paths.user_config_path, f))
        if os.path.exists(user_config_file):
            user = load_yaml(user_config_file, 'config')
            cfg.push_scope('user', user)

        # Environment variable
        env = {}
        for key in defaults:
            envar = 'PYMOD_{}'.format(key.upper())
            if os.getenv(envar):
                env[envar] = os.environ[envar]
        if env:
            cfg.push_scope('environment', env)

    return cfg


config = Singleton(_config)


def get(key, default=None, scope=None):
    """Module-level wrapper for ``Configuration.get()``."""
    return config.get(key, default, scope)


def set(key, value, scope=None):
    """Convenience function for getting single values in config files."""
    return config.set(key, value, scope)




class ConfigError(Exception):
    pass


class ConfigSectionError(Exception):
    pass
