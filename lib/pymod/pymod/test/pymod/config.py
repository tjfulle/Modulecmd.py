import os
import pytest
import pymod.names
import pymod.paths

from pymod.config import Configuration, load_yaml


@pytest.fixture()
def mock_test_config():
    cfg = Configuration()
    config_basename = pymod.names.config_file_basename
    default_config_file = os.path.join(pymod.paths.etc_path, config_basename)
    defaults = load_yaml(default_config_file, 'config')
    cfg.push_scope('defaults', defaults)
    return cfg


def test_config_default(mock_test_config):
    cfg = mock_test_config
    assert cfg.get('debug', scope='defaults') == False
    assert cfg.get('verbose', scope='defaults') == False
    assert cfg.get('default_shell', scope='defaults') == 'bash'
    assert cfg.get('warn_all', scope='defaults') == True
    assert cfg.get('cache_avail', scope='defaults') == True
    assert cfg.get('stop_on_error', scope='defaults') == True
    assert cfg.get('resolve_conflicts', scope='defaults') == False
    assert cfg.get('editor', scope='defaults') == 'vi'
    assert cfg.get('load_after_purge', scope='defaults') == []
    assert cfg.get('strict_modulename_matching', scope='defaults') == False
    assert cfg.get('skip_add_devpack', scope='defaults') == False
    assert cfg.get('color', scope='defaults') == 'auto'


def test_config_user(mock_test_config):
    cfg = mock_test_config
    d = dict(cfg.scopes['defaults'])
    cfg.push_scope('user', d)
    cfg.set('baz', 'spam', scope='user')
    assert cfg.get('baz', scope='user') == 'spam'
    cfg.set('baz', 'spam')
    assert isinstance(cfg.get(None), dict)
    cfg.get(None)
    cfg.get(scope='user')


def test_config_user_unknown_var(mock_test_config):
    cfg = mock_test_config
    d = dict(cfg.scopes['defaults'])
    d['fake config var'] = True
    with pytest.raises(ValueError):
        cfg.push_scope('user', d)


def test_config_user_bad_var_type(mock_test_config):
    cfg = mock_test_config
    d = dict(cfg.scopes['defaults'])
    d['default_shell'] = True
    with pytest.raises(ValueError):
        cfg.push_scope('user', d)
