import os
import pytest
import pymod.names
import pymod.environ


def test_environ_set_get_unset():
    assert pymod.environ.is_empty()
    pymod.environ.set('KEY', 'ONE')
    assert pymod.environ.get('KEY') == 'ONE'
    pymod.environ.unset('KEY')
    assert pymod.environ.get('KEY') is None
    # When a value is unset, it is not removed, but set to None
    assert pymod.environ.get('KEY', 1) is None

    # We didn't set the path, so it will be grabbed from os.environ
    assert pymod.environ.get('PATH') == os.getenv('PATH')


def test_environ_set_alias():
    assert pymod.environ.is_empty()
    pymod.environ.set_alias('A1', 'ls')
    assert len(pymod.environ.environ.aliases) == 1
    assert pymod.environ.environ.aliases['A1'] == 'ls'
    pymod.environ.unset_alias('A1')
    assert len(pymod.environ.environ.aliases) == 1
    assert pymod.environ.environ.aliases['A1'] is None


def test_environ_set_shell_function():
    assert pymod.environ.is_empty()
    pymod.environ.set_shell_function('F1', 'doit "$@"')
    assert len(pymod.environ.environ.shell_functions) == 1
    assert pymod.environ.environ.shell_functions['F1'] == 'doit "$@"'
    pymod.environ.unset_shell_function('F1')
    assert len(pymod.environ.environ.shell_functions) == 1
    assert pymod.environ.environ.shell_functions['F1'] is None


def test_environ_append_path():
    assert pymod.environ.is_empty()
    name = 'PATHNAME'
    pymod.environ.environ[name] = 'bar:baz'
    pymod.environ.append_path(name, 'foo')
    pymod.environ.append_path(name, 'bar')
    pymod.environ.append_path(name, 'baz')
    assert pymod.environ.environ[name] == 'bar:baz:foo'


def test_environ_prepend_path():
    assert pymod.environ.is_empty()
    name = 'PATHNAME'
    pymod.environ.environ[name] = 'bar:baz'
    pymod.environ.prepend_path(name, 'foo')
    pymod.environ.prepend_path(name, 'bar')
    pymod.environ.prepend_path(name, 'baz')
    assert pymod.environ.environ[name] == 'baz:bar:foo'


def test_environ_modulepath_ops():
    """Should not set modulepath directly to environment!"""
    with pytest.raises(ValueError):
        pymod.environ.append_path(pymod.names.modulepath, 'FAKE')
    with pytest.raises(ValueError):
        pymod.environ.prepend_path(pymod.names.modulepath, 'FAKE')
    with pytest.raises(ValueError):
        pymod.environ.remove_path(pymod.names.modulepath, 'FAKE')
    with pytest.raises(ValueError):
        pymod.environ.set(pymod.names.modulepath, 'FAKE')


def test_environ_remove_path():
    assert pymod.environ.is_empty()
    name = 'PATHNAME'
    pymod.environ.environ[name] = 'bar:baz'
    pymod.environ.prepend_path(name, 'foo')
    pymod.environ.prepend_path(name, 'bar')
    pymod.environ.prepend_path(name, 'baz')
    assert pymod.environ.environ[name] == 'baz:bar:foo'
    pymod.environ.remove_path(name, 'baz')
    assert pymod.environ.environ[name] == 'baz:bar:foo'
    pymod.environ.remove_path(name, 'baz')
    assert pymod.environ.environ[name] == 'bar:foo'
    pymod.environ.remove_path(name, 'bar')
    assert pymod.environ.environ[name] == 'bar:foo'
    pymod.environ.remove_path(name, 'bar')
    assert pymod.environ.environ[name] == 'foo'
    pymod.environ.remove_path(name, 'foo')
    assert pymod.environ.environ[name] is None


def test_environ_get_bool():
    assert pymod.environ.is_empty()
    pymod.environ.set('A', '1')
    assert pymod.environ.get_bool('A') == True
    pymod.environ.set('A', 'TRUE')
    assert pymod.environ.get_bool('A') == True
    pymod.environ.set('A', 'ON')
    assert pymod.environ.get_bool('A') == True
    pymod.environ.set('A', '0')
    assert pymod.environ.get_bool('A') == False
    pymod.environ.set('A', 'OFF')
    assert pymod.environ.get_bool('A') == False
    pymod.environ.set('A', 'FALSE')
    assert pymod.environ.get_bool('A') == False


def test_environ_set_env():
    env = pymod.environ.Environ()
    env.set('A', '1')
    pymod.environ.set_env(env)
    assert pymod.environ.get('A') == '1'
