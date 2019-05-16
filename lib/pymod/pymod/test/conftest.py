import os
import re
import py
import pytest
import tempfile

import pymod.names
import pymod.paths
import pymod.config
import pymod.environ
import pymod.modulepath


@pytest.fixture(scope='session', autouse=True)
def os_environ():
    """Cleans out os.environ"""
    real_env = os.environ.copy()
    os.environ.pop(pymod.names.modulepath, None)
    os.environ.pop(pymod.names.loaded_modules, None)
    os.environ.pop(pymod.names.loaded_module_opts, None)
    os.environ.pop(pymod.names.loaded_module_files, None)
    os.environ.pop(pymod.names.loaded_module_refcount, None)
    os.environ.pop(pymod.names.config_file_envar, None)
    to_pop = []
    for (key, val) in os.environ.items():
        if 'pymod' in key.lower():
            to_pop.append(key)
        elif key.startswith(('MODULE_FAMILY_', '_LMMETA_')):
            to_pop.append(key)
    for key in to_pop:
        os.environ.pop(key, None)
    yield os.environ
    os.environ = real_env


@pytest.fixture(scope='function', autouse=True)
def pymod_environ():
    """Mocks up a fake pymod.environ for use by tests."""
    real_environ = pymod.environ.environ
    env = pymod.environ.Environ()
    pymod.environ.environ = env
    yield pymod.environ.environ
    pymod.environ.environ = real_environ


@pytest.fixture(scope='function', autouse=True)
def pymod_swapped_state_reset():
    pymod.mc._mc._swapped_explicitly = []
    pymod.mc._mc._swapped_on_version_change = []
    pymod.mc._mc._swapped_on_family_update = []
    pymod.mc._mc._swapped_on_mp_change = []
    pymod.mc._mc._unloaded_on_mp_change = []


@pytest.fixture(scope='session', autouse=True)
def _mock_modulepath():
    """Session scoped Modulepath object pointing to the mock directory"""
    real_modulepath = pymod.modulepath._path
    path = os.path.join(pymod.paths.mock_modulepath_path, 'core', '1')
    modulepath = pymod.modulepath.Modulepath([path])
    pymod.modulepath._path = modulepath

    yield pymod.modulepath._path

    pymod.modulepath._path = real_modulepath


@pytest.fixture()
def mock_modulepath(request):
    """Function scoped Modulepath object pointing to the mock directory"""
    real_modulepath = pymod.modulepath._path
    def _modulepath(subdir):
        if isinstance(subdir, (tuple, list)):
            path = subdir
        elif os.path.isdir(subdir):
            path = [subdir]
        else:
            p1 = pymod.paths.mock_modulepath_path
            if os.path.isdir(os.path.join(p1, subdir)):
                path = os.path.join(p1, subdir)
            else:
                path = os.path.join(p1, 'core', subdir)
            assert os.path.isdir(path)
            path = [path]
        modulepath = pymod.modulepath.Modulepath(path)
        pymod.modulepath._path = modulepath
        return pymod.modulepath._path
    def _reset():
        pymod.modulepath._path = real_modulepath
    request.addfinalizer(_reset)
    return _modulepath


@pytest.fixture(scope='session', autouse=True)
def mock_config():
    """Removes user defined changes from config"""
    real_configuration = pymod.config.config
    cfg = pymod.config.Configuration()
    basename = pymod.names.config_file_basename
    default_config_file = os.path.join(pymod.paths.etc_path, basename)
    defaults = pymod.config.load_config(default_config_file)
    cfg.push_scope('defaults', defaults)

    dirname = py.path.local(tempfile.mkdtemp())
    pymod.paths.user_config_path = dirname.strpath
    pymod.paths.user_config_platform_path = dirname.mkdir('platform').strpath

    pymod.config.config = cfg

    yield pymod.config.config

    pymod.config.config = real_configuration


@pytest.fixture()
def mock_module():
    class Version:
        def __init__(self, v):
            self.string = v
    class Module:
        def __init__(self, name, version, filename):
            self.name = name
            self.version = Version(version)
            self.filename = filename
    return Module


@pytest.fixture()
def get_loaded_modules():
    def _get_loaded_modules():
        value = pymod.environ.environ.get(pymod.names.loaded_modules, '')
        return [x for x in value.split(os.pathsep) if x.split()]
    return _get_loaded_modules


@pytest.fixture()
def namespace():
    class Namespace:
        pass
    return Namespace


@pytest.fixture()
def modulecmds():
    """Returns a class with members for writing common module commands in to a
    module file"""
    class Commands:
        @staticmethod
        def setenv(key, val=None):
            val = val or key
            return "setenv({0!r}, {1!r})\n".format(key, val)
        @staticmethod
        def unsetenv(key):
            return "unsetenv({0!r})\n".format(key)
        @staticmethod
        def load(x):
            return "load({0!r})\n".format(x)
        @staticmethod
        def load_first(*x):
            x = ','.join('{0!r}'.format(_) for _ in x)
            return "load_first({0})\n".format(x)
        @staticmethod
        def unload(x):
            return "unload({0!r})\n".format(x)
        @staticmethod
        def prepend_path(key, val=None, sep=os.pathsep):
            val = val or key
            return "prepend_path({0!r},{1!r},sep={2!r})\n".format(key, val, sep)
        @staticmethod
        def append_path(key, val=None, sep=os.pathsep):
            val = val or key
            return "append_path({0!r},{1!r},sep={2!r})\n".format(key, val, sep)
        @staticmethod
        def remove_path(key, val=None, sep=os.pathsep):
            val = val or key
            return "remove_path({0!r},{1!r},sep={2!r})\n".format(key, val, sep)
        @staticmethod
        def set_alias(key, val):
            return "set_alias({0!r},{1!r})\n".format(key, val)
        @staticmethod
        def unset_alias(key):
            return "unset_alias({0!r})\n".format(key)
        @staticmethod
        def set_shell_function(key, val):
            return "set_shell_function({0!r},{1!r})\n".format(key, val)
        @staticmethod
        def unset_shell_function(key):
            return "unset_shell_function({0!r})\n".format(key)
        @staticmethod
        def use(path):
            return "use({0!r})\n".format(path)
        @staticmethod
        def unuse(path):
            return "unuse({0!r})\n".format(path)
        @staticmethod
        def swap(a, b):
            return "swap({0!r}, {1!r})\n".format(a, b)
        @staticmethod
        def family(x):
            return "family({0!r})\n".format(x)
        @staticmethod
        def conflict(x):
            return "conflict({0!r})\n".format(x)
        @staticmethod
        def prereq(x):
            return "prereq({0!r})\n".format(x)
        @staticmethod
        def prereq_any(*x):
            x = ','.join('{0!r}'.format(_) for _ in x)
            return "prereq_any({0})\n".format(x)
        @staticmethod
        def source(f):
            return "source({0!r})\n".format(f)
        @staticmethod
        def help(x):
            return "help({0!r})\n".format(x)
        @staticmethod
        def whatis(x):
            return "whatis({0!r})\n".format(x)
        @staticmethod
        def isloaded(x):
            return "is_loaded({0!r})\n".format(x)
    return Commands()
