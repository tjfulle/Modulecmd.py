import os
import sys
try:
    import yaml
except ImportError:
    import tpl.yaml as yaml
import platform
from .trace import trace_calls


class GlobalConfiguration(object):
    def __init__(self):
        # Load default settings
        d = os.path.dirname(os.path.realpath(__file__))
        etc_d = os.path.join(d, '..', '..', 'etc')
        defaults = yaml.load(open(os.path.join(etc_d, 'defaults.yaml')))['pymod']
        self.tests_in_progress = getattr(sys, '_pytest_in_progress_', False)

        if self.tests_in_progress:
            for (key, value) in defaults.items():
                self.set_attribute(key, value)

        else:
            self.dot_dir = os.path.expanduser(
                os.environ.get('PYMOD_DOT_DIR', defaults['dot_dir']))
            # Load user specific settings, if testing not in progress
            user = {}
            files_to_search = (
                os.path.join(self.dot_dir, 'config.yaml'),
                os.path.join(self.dot_dir, platform.uname()[0].lower(), 'config.yaml'),
                os.getenv('PYMOD_CONFIG_FILE'))
            for filename in files_to_search:
                if filename and os.path.isfile(filename):
                    dikt = yaml.load(open(filename))
                    if 'config' not in dikt:
                        s = 'Warning: Unable to find pymod configuration in {0}\n'
                        sys.stderr.write(s.format(filename))
                        continue
                    user.update(dikt['config'])

            # check environment for user specific settings
            for key in defaults:
                if os.getenv('PYMOD_'.format(key.upper())):
                    value = environ['PYMOD_'.format(key.upper())]
                    if value.lower() in ('0', 'false', 'off'):
                        value = False
                    elif value.lower() in ('1', 'true', 'on'):
                        value = True
                    user[key] = value

            for key in defaults:
                value = user.get(key, defaults[key])
                self.set_attribute(key, value)

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

cfg = GlobalConfiguration()
