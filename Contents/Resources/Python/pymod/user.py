import os
import sys
from .utils import import_module_by_filepath
from .cfg import cfg

DEFAULT_DOT_DIR = os.path.expanduser('~/.pymod.d/')

class UserEnv:

    def __init__(self):
        self._m = None
        self.cache = None

    def load(self, dotdir):
        """Return the module defined by user"""

        filename = os.path.join(dotdir, 'module.env')
        if not os.path.isfile(filename):
            return None

        if self._m is not None:
            # We are being reloaded, reset
            for (key, val) in self.cache.items():
                _ = cfg.pop(key, None)
                if val is not None:
                    cfg[key] = val

        self._m = import_module_by_filepath(filename)
        self.cache = {}
        for (key, var) in cfg.items():
            if hasattr(self._m, key) and type(getattr(self._m, key))==type(var):
                self.cache[key] = cfg.get(key)
                cfg[key] = getattr(self._m, key)
        return

    def __getattr__(self, attr):
        return getattr(self._m, attr)

    def empty(self):
        return self._m is None

user_env = UserEnv()

def _dot_dir(memo=[None], reset=0):
    """Return the pymod dot directory, creating it if it is non-existent"""
    if reset or memo[0] is None:
        dirname = os.getenv('PYMOD_DOT_DIR', DEFAULT_DOT_DIR)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        memo[0] = str(dirname)
        if not hasattr(sys, '_pytest_in_progress_'):
            user_env.load(memo[0])
        else:
            if dirname != DEFAULT_DOT_DIR:
                user_env.load(memo[0])
            else:
                memo[0] = None
    return memo[0]


def pymod_env_key(item, isolate=None):
    if isolate is None:
        isolate = os.getenv('__PYMOD_ISOLATED__') == '1'
    key = item if not isolate else '__PYMOD_{0}__'.format(item.strip('_'))
    return key


