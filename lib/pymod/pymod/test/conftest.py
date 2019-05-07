import os
import pytest

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


@pytest.fixture(scope='session', autouse=True)
def _mock_modulepath():
    """Session scoped Modulepath object pointing to the mock directory"""
    real_modulepath = pymod.modulepath.mpath
    path = os.path.join(pymod.paths.mock_modulepath_path, 'core', '1')
    modulepath = pymod.modulepath.Modulepath([path])
    pymod.modulepath.mpath = modulepath

    yield pymod.modulepath.mpath

    pymod.modulepath.mpath = real_modulepath


@pytest.fixture()
def mock_modulepath(request):
    """Function scoped Modulepath object pointing to the mock directory"""
    real_modulepath = pymod.modulepath.mpath
    def _modulepath(subdir):
        if os.path.isdir(subdir):
            path = subdir
        else:
            p1 = pymod.paths.mock_modulepath_path
            if os.path.isdir(os.path.join(p1, subdir)):
                path = os.path.join(p1, subdir)
            else:
                path = os.path.join(p1, 'core', subdir)
        assert os.path.isdir(path)
        modulepath = pymod.modulepath.Modulepath([path])
        pymod.modulepath.mpath = modulepath
        return pymod.modulepath.mpath
    def _reset():
        pymod.modulepath.mpath = real_modulepath
    request.addfinalizer(_reset)
    return _modulepath


@pytest.fixture(scope='session', autouse=True)
def mock_config():
    """Removes user defined changes from config"""
    real_configuration = pymod.config.config
    cfg = pymod.config.Configuration()
    f = pymod.names.config_filename
    default_config_file = os.path.join(pymod.paths.etc_path, f)
    defaults = pymod.config.load_yaml(default_config_file, 'config')
    cfg.push_scope('defaults', defaults)
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
