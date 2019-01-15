import os
import sys
try:
    import yaml
except ImportError:
    import tpl.yaml as yaml
from .trace import trace_calls


class GlobalConfiguration(object):
    def __init__(self):
        # Load default settings

        d = os.path.dirname(os.path.realpath(__file__))
        etc_d = os.path.join(d, '..', '..', 'etc')
        defaults = self.read_config(os.path.join(etc_d, 'config.yaml'))
        if defaults is None:
            raise Exception('Default configuration has been moved!')

        # Load user specific settings, if testing not in progress
        user_cfg = {}
        self.tests_in_progress = getattr(sys, '_pytest_in_progress_', False)
        if not self.tests_in_progress:

            default_d = '~/.pymod.d'
            d_from_env = os.getenv('PYMOD_DOT_DIR')
            self.dot_dir = os.path.expanduser(d_from_env or default_d)
            user_cfg.update(self.load_user_cfg(self.dot_dir))

            # check environment for user specific settings
            for key in defaults:
                envar = 'pymod_{0}'.format(key)
                if os.getenv(envar):
                    value = os.environ[envar]
                elif os.getenv(envar.upper()):
                    value = os.environ[envar.upper()]
                else:
                    continue
                if value.lower() in ('0', 'false', 'off'):
                    value = False
                elif value.lower() in ('1', 'true', 'on'):
                    value = True
                elif not value.split():
                    value = None
                user_cfg[key] = value

        for (key, value) in defaults.items():
            value = user_cfg.get(key, value)
            self.set_attribute(key, value)

    def load_user_cfg(self, dirname):
        def warn(s):
            sys.stderr.write('Modulecmd.py: warning: ' + s + '\n')

        user_cfg = {}

        # check default
        filename = os.path.join(dirname, 'config.yaml')
        if os.path.isfile(filename):
            __cfg = self.read_config(filename)
            if __cfg is None:
                warn("{0!r} does not define a 'config' entry".format(filename))
            else:
                user_cfg.update(__cfg)

        # Check environment variable
        filename = os.environ.get('PYMOD_CONFIG_FILE', os.getenv('pymod_config_file'))
        if filename:
            if not os.path.isfile(filename):
                warn('config file {0!r} does not exist'.format(filename))
            else:
                __cfg = self.read_config(filename)
                if __cfg is None:
                    warn("{0!r} does not define a 'config' entry".format(filename))
                else:
                    user_cfg.update(__cfg)

        return user_cfg

    @staticmethod
    def config_key(filename):
        return os.path.splitext(os.path.basename(filename))[0]

    @staticmethod
    def read_config(filename, key='config'):
        dikt = yaml.load(open(filename))
        return dikt.get(key)

    def set_attribute(self, name, value):
        object.__setattr__(self, name, value)

    @property
    def verbosity(self):
        return self._verbosity

    @verbosity.setter
    def verbosity(self, arg):
        if arg > 2:
            sys.settrace(trace_calls)
        self._verbosity = arg

    @property
    def dotdir(self):
        return self._dot_dir

    @property
    def dot_dir(self):
        return self._dot_dir

    @dot_dir.setter
    def dot_dir(self, arg):
        if arg is None:
            self._dot_dir = None
        else:
            dirname = os.path.expanduser(arg)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
            self._dot_dir = dirname

    @property
    def collections_filename(self):
        return os.path.join(self.dot_dir, self._collections_filename)

    @collections_filename.setter
    def collections_filename(self, arg):
        self._collections_filename = arg

    @property
    def clones_filename(self):
        return os.path.join(self.dot_dir, self._clones_filename)

    @clones_filename.setter
    def clones_filename(self, arg):
        self._clones_filename = arg

    @property
    def tests_in_progress(self):
        return self._tests_in_progress

    @tests_in_progress.setter
    def tests_in_progress(self, arg):
        self._tests_in_progress = bool(arg)

    @property
    def user_env_filename(self):
        return os.path.join(self.dot_dir, self._user_env_filename)

    @user_env_filename.setter
    def user_env_filename(self, arg):
        self._user_env_filename = arg

    @property
    def load_after_purge(self):
        return self._load_after_purge

    @load_after_purge.setter
    def load_after_purge(self, arg):
        if arg is not None:
            arg = [x.strip() for x in arg.split(',') if x.split()]
        self._load_after_purge = arg

    @property
    def color_output(self):
        return self._color_output

    @color_output.setter
    def color_output(self, arg):
        if arg is None:
            arg = 'never'
        if not arg in ('always', 'auto', 'never'):
            raise ValueError('color: must be one of always, auto, never')
        self._color_output = arg

cfg = GlobalConfiguration()
