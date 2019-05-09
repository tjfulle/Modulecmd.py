import os
import pymod.paths
import pymod.config
from llnl.util.lang import load_module_from_file, Singleton


class UserEnv:
    def __init__(self, filename):
        # Load user module, if found
        self._module = load_module_from_file('pymod._user', filename)

    def __getattr__(self, attr):
        if self._module is None:
            return None
        return getattr(self._module, attr)


def _user_env():
    name = pymod.config.get('user_env_filename')
    if os.path.exists(name):
        filename = name
    elif os.path.exists(os.path.join(pymod.paths.user_config_path, name)):
        filename = os.path.join(pymod.paths.user_config_path, name)
    elif os.path.exists(os.path.join(pymod.paths.user_config_path, 'user.py')):
        filename = os.path.join(pymod.paths.user_config_path, 'user.py')
    else:
        filename = None
    if filename is not None:
        assert os.path.isfile(os.path.realpath(filename))
    return UserEnv(filename)


env = Singleton(_user_env)
