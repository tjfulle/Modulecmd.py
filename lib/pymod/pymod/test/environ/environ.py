import pytest
import pymod.environ


def test_set_get_unset():
    assert pymod.environ.is_empty()
    pymod.environ.set('KEY', 'ONE')
    assert pymod.environ.get('KEY') == 'ONE'
    pymod.environ.unset('KEY')
    assert pymod.environ.get('KEY') is None
    # When a value is unset, it is not removed, but set to None
    assert pymod.environ.get('KEY', 1) is None


def test_set_alias():
    assert pymod.environ.is_empty()
    pymod.environ.set_alias('A1', 'ls')
    assert len(pymod.environ.environ.aliases) == 1
    assert pymod.environ.environ.aliases['A1'] == 'ls'
    pymod.environ.unset_alias('A1')
    assert len(pymod.environ.environ.aliases) == 1
    assert pymod.environ.environ.aliases['A1'] is None


def test_set_shell_function():
    assert pymod.environ.is_empty()
    pymod.environ.set_shell_function('F1', 'doit "$@"')
    assert len(pymod.environ.environ.shell_functions) == 1
    assert pymod.environ.environ.shell_functions['F1'] == 'doit "$@"'
    pymod.environ.unset_shell_function('F1')
    assert len(pymod.environ.environ.shell_functions) == 1
    assert pymod.environ.environ.shell_functions['F1'] is None


def test_append_path():
    assert pymod.environ.is_empty()
    name = 'PATHNAME'
    pymod.environ.environ[name] = 'bar:baz'
    pymod.environ.append_path(name, 'foo')
    pymod.environ.append_path(name, 'bar')
    pymod.environ.append_path(name, 'baz')
    assert pymod.environ.environ[name] == 'bar:baz:foo'


def test_prepend_path():
    assert pymod.environ.is_empty()
    name = 'PATHNAME'
    pymod.environ.environ[name] = 'bar:baz'
    pymod.environ.prepend_path(name, 'foo')
    pymod.environ.prepend_path(name, 'bar')
    pymod.environ.prepend_path(name, 'baz')
    assert pymod.environ.environ[name] == 'baz:bar:foo'


def test_remove_path():
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
