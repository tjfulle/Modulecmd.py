import os
import py
import pytest
import tempfile

import modulecmd.system
import modulecmd.cache
import modulecmd.names
import modulecmd.paths
import modulecmd.config
import modulecmd.environ
import modulecmd.modulepath
from modulecmd.util import singleton


@pytest.fixture(autouse=True)
def no_dump(monkeypatch):
    def mock_dump(stream=None):
        with open(os.devnull, "a") as stream:
            output = modulecmd.environ.format_output()
            stream.write(output)
            output = modulecmd.system.state.format_changes()
            if output.split():
                stream.write(output)

    monkeypatch.delattr(modulecmd.system, "dump")
    modulecmd.system.dump = mock_dump


@pytest.fixture(scope="function", autouse=True)
def os_environ():
    """Cleans out os.environ"""
    orig_env = os.environ.copy()
    os.environ.pop(modulecmd.names.modulepath, None)
    os.environ.pop(modulecmd.names.initial_env, None)
    os.environ.pop(modulecmd.names.loaded_modules, None)
    os.environ.pop(modulecmd.names.loaded_module_files, None)
    os.environ.pop(modulecmd.names.sourced_files, None)
    keys = [
        _
        for _ in list(os.environ.keys())
        if _.startswith(modulecmd.names.loaded_module_cellar)
    ]
    for key in keys:
        os.environ.pop(key, None)
    to_pop = []
    keys_to_pop = (modulecmd.names.loaded_module_meta(""), modulecmd.names.family_name(""))
    for (key, val) in os.environ.items():
        if "modulecmd" in key.lower():
            to_pop.append(key)
        elif key.startswith(keys_to_pop):
            to_pop.append(key)
    for key in to_pop:
        os.environ.pop(key, None)
    yield os.environ
    os.environ = orig_env


@pytest.fixture(scope="function", autouse=True)
def modulecmd_cache():
    """Mocks up a fake modulecmd.cache for use by tests."""
    modulecmd.cache.cache = singleton(modulecmd.cache.factory)


@pytest.fixture(scope="function", autouse=True)
def modulecmd_environ():
    """Mocks up a fake modulecmd.environ for use by tests."""
    orig_environ = modulecmd.environ.environ
    env = modulecmd.environ.Environ()
    modulecmd.environ.environ = env
    yield modulecmd.environ.environ
    modulecmd.environ.environ = orig_environ


@pytest.fixture(scope="function", autouse=True)
def modulecmd_global_state_reset():
    modulecmd.system.state._loaded_modules = None
    modulecmd.system.state._swapped_explicitly = []
    modulecmd.system.state._swapped_on_version_change = []
    modulecmd.system.state._swapped_on_family_update = []
    modulecmd.system.state._swapped_on_mp_change = []
    modulecmd.system.state._unloaded_on_mp_change = []


@pytest.fixture()
def mock_modulepath(request):
    """Function scoped Modulepath object pointing to the mock directory"""
    real_modulepath = modulecmd.modulepath._path

    def _modulepath(subdir):
        if isinstance(subdir, (tuple, list)):
            path = subdir
        elif os.path.isdir(subdir):
            path = [subdir]
        else:
            raise TypeError("Unknown subdir type")
        modulepath = modulecmd.modulepath.Modulepath(path)
        modulecmd.modulepath._path = modulepath
        return modulecmd.modulepath._path

    def _reset():
        modulecmd.modulepath._path = real_modulepath

    request.addfinalizer(_reset)
    return _modulepath


@pytest.fixture(scope="session", autouse=True)
def mock_config():
    """Removes user defined changes from config"""
    os.environ.pop("MODULECMD_CONFIG_DIR", None)
    real_configuration = modulecmd.config._config
    cfg = modulecmd.config.configuration()
    dirname = py.path.local(tempfile.mkdtemp())
    modulecmd.paths.user_config_path = dirname.strpath
    modulecmd.paths.user_cache_path = dirname.strpath
    modulecmd.config._config = cfg
    yield modulecmd.config._config
    modulecmd.config._config = real_configuration


@pytest.fixture()
def mock_module():
    class Version:
        def __init__(self, v):
            self.string = v

    class Module:
        def __init__(self, name, version, filename):
            self.name = name
            self.version = Version(version)
            self.file = filename

    return Module


@pytest.fixture()
def get_loaded_modules():
    def _get_loaded_modules():
        value = modulecmd.environ.environ.get(modulecmd.names.loaded_modules, "")
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
            x = ",".join("{0!r}".format(_) for _ in x)
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
            x = ",".join("{0!r}".format(_) for _ in x)
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
