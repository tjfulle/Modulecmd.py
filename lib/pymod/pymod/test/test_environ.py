import pymod.environ as environ


def unit_test():
    environ.set('KEY', 'ONE')
    assert environ.get('KEY') == 'ONE'
    environ.unset('KEY')
    assert environ.get('KEY') is None
    # When a value is unset, it is not removed, but set to None
    assert environ.get('KEY', 1) is None
    environ.reset()


def test_set_alias():
    environ.set_alias('A1', 'ls')
    assert len(environ.environ.aliases) == 1
    assert environ.environ.aliases['A1'] == 'ls'
    environ.unset_alias('A1')
    assert len(environ.environ.aliases) == 1
    assert environ.environ.aliases['A1'] is None
    environ.reset()


def test_set_shell_function():
    environ.set_shell_function('F1', 'doit "$@"')
    assert len(environ.environ.shell_functions) == 1
    assert environ.environ.shell_functions['F1'] == 'doit "$@"'
    environ.unset_shell_function('F1')
    assert len(environ.environ.shell_functions) == 1
    assert environ.environ.shell_functions['F1'] is None
    environ.reset()


def test_append_path():
    name = 'PATHNAME'
    environ.environ[name] = 'bar:baz'
    environ.append_path(name, 'foo')
    environ.append_path(name, 'bar')
    environ.append_path(name, 'baz')
    assert environ.environ[name] == 'bar:baz:foo'
    environ.reset()


def test_prepend_path():
    name = 'PATHNAME'
    environ.environ[name] = 'bar:baz'
    environ.prepend_path(name, 'foo')
    environ.prepend_path(name, 'bar')
    environ.prepend_path(name, 'baz')
    assert environ.environ[name] == 'baz:bar:foo'
    environ.reset()


def test_remove_path():
    name = 'PATHNAME'
    environ.environ[name] = 'bar:baz'
    environ.prepend_path(name, 'foo')
    environ.prepend_path(name, 'bar')
    environ.prepend_path(name, 'baz')
    assert environ.environ[name] == 'baz:bar:foo'
    environ.remove_path(name, 'baz')
    assert environ.environ[name] == 'baz:bar:foo'
    environ.remove_path(name, 'baz')
    assert environ.environ[name] == 'bar:foo'
    environ.remove_path(name, 'bar')
    assert environ.environ[name] == 'bar:foo'
    environ.remove_path(name, 'bar')
    assert environ.environ[name] == 'foo'
    environ.remove_path(name, 'foo')
    assert environ.environ[name] is None
    environ.reset()
