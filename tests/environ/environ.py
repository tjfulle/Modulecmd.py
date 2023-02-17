import os
import pytest
import modulecmd.names
import modulecmd.environ
from modulecmd.util import boolean


def test_environ_set_get_unset():
    assert modulecmd.environ.is_empty()
    modulecmd.environ.set("KEY", "ONE")
    assert modulecmd.environ.get("KEY") == "ONE"
    modulecmd.environ.unset("KEY")
    assert modulecmd.environ.get("KEY") is None
    # When a value is unset, it is not removed, but set to None
    assert modulecmd.environ.get("KEY", 1) is None

    # We didn't set the path, so it will be grabbed from os.environ
    assert modulecmd.environ.get("PATH") == os.getenv("PATH")


def test_environ_set_alias():
    assert modulecmd.environ.is_empty()
    modulecmd.environ.set_alias("A1", "ls")
    assert len(modulecmd.environ.environ.aliases) == 1
    assert modulecmd.environ.environ.aliases["A1"] == "ls"
    modulecmd.environ.unset_alias("A1")
    assert len(modulecmd.environ.environ.aliases) == 1
    assert modulecmd.environ.environ.aliases["A1"] is None


def test_environ_set_shell_function():
    assert modulecmd.environ.is_empty()
    modulecmd.environ.set_shell_function("F1", 'doit "$@"')
    assert len(modulecmd.environ.environ.shell_functions) == 1
    assert modulecmd.environ.environ.shell_functions["F1"] == 'doit "$@"'
    modulecmd.environ.unset_shell_function("F1")
    assert len(modulecmd.environ.environ.shell_functions) == 1
    assert modulecmd.environ.environ.shell_functions["F1"] is None


def test_environ_append_path():
    assert modulecmd.environ.is_empty()
    name = "PATHNAME"
    modulecmd.environ.environ[name] = "bar:baz"
    modulecmd.environ.append_path(name, "foo")
    modulecmd.environ.append_path(name, "bar")
    modulecmd.environ.append_path(name, "baz")
    assert modulecmd.environ.environ[name] == "bar:baz:foo"


def test_environ_prepend_path():
    assert modulecmd.environ.is_empty()
    name = "PATHNAME"
    modulecmd.environ.environ[name] = "bar:baz"
    modulecmd.environ.prepend_path(name, "foo")
    modulecmd.environ.prepend_path(name, "bar")
    modulecmd.environ.prepend_path(name, "baz")
    assert modulecmd.environ.environ[name] == "baz:bar:foo"
    assert modulecmd.environ.get_path(name) == ["baz", "bar", "foo"]


def test_environ_modulepath_ops():
    """Should not set modulepath directly to environment!"""
    with pytest.raises(ValueError):
        modulecmd.environ.append_path(modulecmd.names.modulepath, "FAKE")
    with pytest.raises(ValueError):
        modulecmd.environ.prepend_path(modulecmd.names.modulepath, "FAKE")
    with pytest.raises(ValueError):
        modulecmd.environ.remove_path(modulecmd.names.modulepath, "FAKE")
    with pytest.raises(ValueError):
        modulecmd.environ.set(modulecmd.names.modulepath, "FAKE")
    with pytest.raises(ValueError):
        modulecmd.environ.unset(modulecmd.names.modulepath)


def test_environ_remove_path():
    assert modulecmd.environ.is_empty()
    name = "PATHNAME"
    modulecmd.environ.environ[name] = "bar:baz"
    modulecmd.environ.prepend_path(name, "foo")
    modulecmd.environ.prepend_path(name, "bar")
    modulecmd.environ.prepend_path(name, "baz")
    assert modulecmd.environ.environ[name] == "baz:bar:foo"
    modulecmd.environ.remove_path(name, "baz")
    assert modulecmd.environ.environ[name] == "baz:bar:foo"
    modulecmd.environ.remove_path(name, "baz")
    assert modulecmd.environ.environ[name] == "bar:foo"
    modulecmd.environ.remove_path(name, "bar")
    assert modulecmd.environ.environ[name] == "bar:foo"
    modulecmd.environ.remove_path(name, "bar")
    assert modulecmd.environ.environ[name] == "foo"
    modulecmd.environ.remove_path(name, "foo")
    assert modulecmd.environ.environ[name] is None


def test_environ_get_with_type():
    assert modulecmd.environ.is_empty()
    modulecmd.environ.set("A", "1")
    assert modulecmd.environ.get("A", type=boolean) == True
    modulecmd.environ.set("A", "TRUE")
    assert modulecmd.environ.get("A", type=boolean) == True
    modulecmd.environ.set("A", "ON")
    assert modulecmd.environ.get("A", type=boolean) == True
    modulecmd.environ.set("A", "0")
    assert modulecmd.environ.get("A", type=boolean) == False
    modulecmd.environ.set("A", "OFF")
    assert modulecmd.environ.get("A", type=boolean) == False
    modulecmd.environ.set("A", "FALSE")
    assert modulecmd.environ.get("A", type=boolean) == False


def test_environ_set_env():
    env = modulecmd.environ.Environ()
    env.set("A", "1")
    modulecmd.environ.set_env(env)
    assert modulecmd.environ.get("A") == "1"


def test_environ_set_serialized_dict():
    modulecmd.environ.set("A", {"a": 1}, serialize=True)
    assert modulecmd.environ.get("A", serialized=True) == {"a": 1}


def test_environ_set_serialized_list():
    modulecmd.environ.set("A", [0, 1], serialize=True)
    assert modulecmd.environ.get("A", serialized=True) == [0, 1]


def test_environ_set_serialized_None():
    modulecmd.environ.set("A", None, serialize=True)
    assert modulecmd.environ.get("A", serialized=True) is None


def test_environ_set_get_path():
    assert modulecmd.environ.is_empty()
    path = ["baz", "bar"]
    modulecmd.environ.set_path("A", path)
    assert modulecmd.environ.get("A") == "baz:bar"
    assert modulecmd.environ.get_path("A") == ["baz", "bar"]

    modulecmd.environ.set_path("A", path, sep="@")
    assert modulecmd.environ.get("A") == "baz@bar"
    assert modulecmd.environ.get_path("A", sep="@") == ["baz", "bar"]


def test_environ_factory():
    environ = modulecmd.environ.factory()
    assert isinstance(environ, modulecmd.environ.Environ)


def test_environ_ld_library_path():
    key = "LD_LIBRARY_PATH"
    fixed = modulecmd.environ.environ.fix_ld_library_path(key)
    assert fixed == modulecmd.names.platform_ld_library_path

    key = "CRAY_LD_LIBRARY_PATH"
    fixed = modulecmd.environ.environ.fix_ld_library_path(key)
    assert fixed == key
