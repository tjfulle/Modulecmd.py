import os
import sys
from .utils import import_module_by_filepath
from .config import cfg

class UserEnv:
    def __init__(self):
        # Load user module, if found
        self._m = None
        if not cfg.tests_in_progress:
            self.load()

    def load(self, filename=None):
        self._m = None
        if filename is None:
            filename = cfg.user_env_filename
        if os.path.isfile(filename):
            self._m = import_module_by_filepath(filename)

    def __getattr__(self, attr):
        if self._m is None:
            return None
        return getattr(self._m, attr)

    def empty(self):
        return self._m is None

user_env = UserEnv()
