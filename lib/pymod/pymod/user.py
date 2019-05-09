import os
import pymod.config
import pymod.names
import pymod.paths
from llnl.util.lang import load_module_from_file, Singleton


class UserEnv:
    def __init__(self, filename):
        # Load user module, if found
        if filename is None:
            self._module = None
        else:
            self._module = load_module_from_file('pymod._user', filename)

    def __getattr__(self, attr):
        if self._module is None:
            return None
        return getattr(self._module, attr)


def _user_env():
    basename = pymod.names.user_env_file_basename
    for dirname in (pymod.paths.user_config_platform_path,
                    pymod.paths.user_config_path):
        if os.path.exists(os.path.join(dirname, basename)):
            filename = os.path.join(dirname, basename)
            break
    else:
        filename = None
    if filename is not None:
        assert os.path.isfile(os.path.realpath(filename))
    return UserEnv(filename)


env = Singleton(_user_env)
