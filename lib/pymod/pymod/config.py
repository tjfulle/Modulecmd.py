import os
import ruamel.yaml as yaml
import pymod.paths
import pymod.names
from llnl.util.lang import Singleton
from spack.util.executable import which


def load_config(filename):
    dict = yaml.load(open(filename))
    return dict.get('config')


has_tclsh = which('tclsh') is not None


class Configuration(object):
    scope_names = ['defaults', 'user', 'environment', 'command_line']
    def __init__(self):
        self.scopes = {}

    def push_scope(self, scope_name, data):
        """Add a scope to the Configuration."""
        if 'defaults' in self.scopes and scope_name != 'defaults':
            self.verify_config(data)
        self.scopes.setdefault(scope_name, {}).update(dict(data))

    def verify_config(self, data):
        for (key, val) in data.items():
            try:
                default = self.scopes['defaults'][key]
            except KeyError:
                msg = 'Unknown user config var {0!r}'.format(key)
                raise ValueError(msg)
            if type(default) != type(val):
                m = 'User config var {0!r} must be of type {1!r}, not {2!r}'
                msg = m.format(key, type(default).__name__, type(val).__name__)
                raise ValueError(msg)

    def remove_scope(self, scope_name):
        return self.scopes.pop(scope_name, None)

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

    def set(self, key, value, scope=None):  # pragma: no cover
        if scope is not None:
            self.scopes.setdefault(scope, {}).update({key: value})
        else:
            for scope_name in self.scope_names[::-1]:
                self.scopes.setdefault(scope_name, {}).update({key: value})

def factory():
    """Singleton Configuration instance.

    This constructs one instance associated with this module and returns
    it. It is bundled inside a function so that configuratoin can be
    initialized lazily.

    Returns
    -------
    cfg : Configuration
        object for accessing Modulecmd.py configuration

    """
    cfg = Configuration()

    config_basename = pymod.names.config_file_basename

    default_config_file = os.path.join(
        pymod.paths.etc_path, 'defaults', config_basename)
    defaults = load_config(default_config_file)
    cfg.push_scope('defaults', defaults)

    admin_config_file = os.path.join(
        pymod.paths.etc_path, config_basename)
    if os.path.isfile(admin_config_file):  # pragma: no cover
        admin = load_config(admin_config_file)
        cfg.push_scope('user', admin)

    user_config_file = os.getenv(pymod.names.config_file_envar)
    if user_config_file is not None:  # pragma: no cover
        user = load_config(user_config_file)
        cfg.push_scope('user', user)

    else:  # pragma: no cover
        for dirname in (pymod.paths.user_config_path,
                        pymod.paths.user_config_platform_path):
            user_config_file = os.path.join(dirname, config_basename)
            if os.path.exists(user_config_file):
                user = load_config(user_config_file)
                cfg.push_scope('user', user)

    # Environment variable
    env = {}
    for key in defaults:  # pragma: no cover
        envar = 'PYMOD_{0}'.format(key.upper())
        if envar in ('PYMOD_CONFIG_DIR',
                     'PYMOD_PLATFORM_CONFIG_DIR',
                     'PYMOD_CONFIG_FILE'):
            continue
        if os.getenv(envar):
            env[envar] = os.environ[envar]

    if env:  # pragma: no cover
        cfg.push_scope('environment', env)

    return cfg


config = Singleton(factory)


def get(key, default=None, scope=None):
    """Module-level wrapper for ``Configuration.get()``."""
    return config.get(key, default, scope)


def set(key, value, scope=None):  # pragma: no cover
    """Convenience function for getting single values in config files."""
    return config.set(key, value, scope)


class ConfigError(Exception):
    pass


class ConfigSectionError(Exception):
    pass
