import os
import sys
import pymod.config
import pymod.names
import pymod.paths
from llnl.util.lang import load_module_from_file, Singleton


class UserEnv:
    def __init__(self, filename):
        # Load user module, if found
        if filename is None:
            self._module = None
            self._modulename = None
        else:
            modulename = "pymod._{0}".format(
                os.path.splitext(os.path.basename(filename))[0]
            )
            self._module = load_module_from_file(modulename, filename)
            assert self._module is not None
            self._modulename = modulename

    def __getattr__(self, attr):
        if self._module is None:  # pragma: no cover
            return None
        return getattr(self._module, attr)


def factory():
    basename = pymod.names.user_env_file_basename
    f = pymod.paths.join_user(basename)
    filename = f if os.path.isfile(f) else None
    return UserEnv(filename)


def set_user_env(user_env):
    global env
    assert isinstance(user_env, UserEnv)
    env = user_env


def reset():  # pragma: no cover
    global env
    if env._modulename in sys.modules:
        del sys.modules[env._modulename]
    env = factory()


env = Singleton(factory)
