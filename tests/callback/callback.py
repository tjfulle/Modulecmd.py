import os
import pytest

import modulecmd.system
import modulecmd.error
import modulecmd.modes
import modulecmd.environ
import modulecmd.callback
from modulecmd.callback import get_callback

"""Test of the callback functions sent to modules"""


def test_callback_all_callback():
    all_callbacks = modulecmd.callback.all_callbacks()


def test_callback_path_ops():
    append_path = get_callback("append_path")
    prepend_path = get_callback("prepend_path")
    remove_path = get_callback("remove_path")

    append_path(None, modulecmd.modes.load, "foo", "bar", sep=";")
    prepend_path(None, modulecmd.modes.load, "foo", "baz", sep=";")
    assert modulecmd.environ.get("foo") == "baz;bar"
    remove_path(None, modulecmd.modes.load, "foo", "bar", sep=";")
    remove_path(None, modulecmd.modes.load, "foo", "baz", sep=";")
    assert modulecmd.environ.get("foo") is None

    append_path(None, modulecmd.modes.load, "foo", "bar", sep=";")
    prepend_path(None, modulecmd.modes.load, "foo", "baz", sep=";")
    assert modulecmd.environ.get("foo") == "baz;bar"
    append_path(None, modulecmd.modes.unload, "foo", "bar", sep=";")
    prepend_path(None, modulecmd.modes.unload, "foo", "baz", sep=";")
    assert modulecmd.environ.get("foo") is None


def test_callback_conflict(tmpdir, mock_modulepath):
    conflict = get_callback("conflict")
    tmpdir.join("a.py").write("")
    tmpdir.join("b.py").write("")
    mock_modulepath(tmpdir.strpath)
    a = modulecmd.modulepath.get("a")

    b = modulecmd.system.load("b")
    x = modulecmd.config.get("resolve_conflicts")
    modulecmd.config.set("resolve_conflicts", False)
    with pytest.raises(modulecmd.error.ModuleConflictError):
        conflict(a, modulecmd.modes.load, "b")

    modulecmd.config.set("resolve_conflicts", True)
    conflict(a, modulecmd.modes.load, "b")

    modulecmd.config.set("resolve_conflicts", x)

    b = modulecmd.system.unload("b")
    conflict(a, modulecmd.modes.load, "b")


def test_callback_prereq(tmpdir, mock_modulepath):
    prereq = get_callback("prereq")
    prereq_any = get_callback("prereq_any")
    tmpdir.join("a.py").write("")
    tmpdir.join("b.py").write("")
    mock_modulepath(tmpdir.strpath)

    with pytest.raises(modulecmd.error.PrereqMissingError):
        prereq(None, modulecmd.modes.load, "b")

    modulecmd.system.load("b")
    prereq(None, modulecmd.modes.load, "b")
    prereq(None, modulecmd.modes.load, "name:b")
    prereq_any(None, modulecmd.modes.load, "x", "y", "b")
    prereq_any(None, modulecmd.modes.load, "x", "y", "name:b")
    with pytest.raises(modulecmd.error.PrereqMissingError):
        prereq_any(None, modulecmd.modes.load, "x", "y", "z")

    with pytest.raises(Exception):
        # Foo is not a recognized prefix
        prereq(None, modulecmd.modes.load, "foo:b")


def test_callback_set_alias():
    set_alias = get_callback("set_alias")
    unset_alias = get_callback("unset_alias")

    set_alias(None, modulecmd.modes.load, "foo", "bar")
    assert modulecmd.environ.environ.aliases["foo"] == "bar"
    set_alias(None, modulecmd.modes.unload, "foo", "bar")
    assert modulecmd.environ.environ.aliases["foo"] is None

    set_alias(None, modulecmd.modes.load, "foo", "bar")
    assert modulecmd.environ.environ.aliases["foo"] == "bar"
    unset_alias(None, modulecmd.modes.load, "foo")
    assert modulecmd.environ.environ.aliases["foo"] is None

    set_alias(None, modulecmd.modes.load, "foo", "bar")
    assert modulecmd.environ.environ.aliases["foo"] == "bar"
    unset_alias(None, modulecmd.modes.unload, "foo")
    assert modulecmd.environ.environ.aliases["foo"] == "bar"


def test_callback_set_shell_function():
    set_shell_function = get_callback("set_shell_function")
    unset_shell_function = get_callback("unset_shell_function")

    set_shell_function(None, modulecmd.modes.load, "foo", "bar")
    assert modulecmd.environ.environ.shell_functions["foo"] == "bar"
    set_shell_function(None, modulecmd.modes.unload, "foo", "bar")
    assert modulecmd.environ.environ.shell_functions["foo"] is None

    set_shell_function(None, modulecmd.modes.load, "foo", "bar")
    assert modulecmd.environ.environ.shell_functions["foo"] == "bar"
    unset_shell_function(None, modulecmd.modes.load, "foo")
    assert modulecmd.environ.environ.shell_functions["foo"] is None

    set_shell_function(None, modulecmd.modes.load, "foo", "bar")
    assert modulecmd.environ.environ.shell_functions["foo"] == "bar"
    unset_shell_function(None, modulecmd.modes.unload, "foo")
    assert modulecmd.environ.environ.shell_functions["foo"] == "bar"


def test_callback_source(tmpdir, capsys):
    baz = tmpdir.join("baz")
    baz.write("echo BAZ")
    source = get_callback("source")
    source(None, modulecmd.modes.load, baz.strpath)
    assert len(modulecmd.environ.environ.files_to_source) == 1
    assert modulecmd.environ.environ.files_to_source[0][0] == baz.strpath
    with pytest.raises(ValueError):
        source(None, modulecmd.modes.load, "fake.txt")


def test_callback_load(tmpdir, mock_modulepath):
    load = get_callback("load")
    swap = get_callback("swap")
    unload = get_callback("unload")
    load_first = get_callback("load_first")

    tmpdir.join("a.py").write("")
    mock_modulepath(tmpdir.strpath)

    with pytest.raises(modulecmd.error.ModuleNotFoundError):
        load(None, modulecmd.modes.load, "x")

    with pytest.raises(modulecmd.error.ModuleNotFoundError):
        load(None, modulecmd.modes.load, "x")

    # Even though `x` is not a module, unloading does not throw
    unload(None, modulecmd.modes.load, "x")

    load(None, modulecmd.modes.load, "a")
    a = modulecmd.modulepath.get("a")
    assert a.is_loaded

    unload(None, modulecmd.modes.load, "a")
    assert not a.is_loaded

    load(None, modulecmd.modes.unload, "a")
    assert not a.is_loaded

    load(None, modulecmd.modes.load, "a")
    assert a.is_loaded

    unload(None, modulecmd.modes.unload, "a")
    assert a.is_loaded

    with pytest.raises(modulecmd.error.ModuleNotFoundError):
        load_first(None, modulecmd.modes.load, "x", "y", "z")
    load_first(None, modulecmd.modes.load, "x", "y", "z", None)
    load_first(None, modulecmd.modes.load, "x", "y", "a")
    a = modulecmd.modulepath.get("a")
    assert a.is_loaded


def test_callback_swap(tmpdir, mock_modulepath):
    swap = get_callback("swap")
    tmpdir.join("a.py").write("")
    tmpdir.join("b.py").write("")
    mock_modulepath(tmpdir.strpath)

    a = modulecmd.system.load("a")
    assert a.is_loaded

    b = modulecmd.modulepath.get("b")
    assert not b.is_loaded

    swap(None, modulecmd.modes.unload, "a", "b")
    assert a.is_loaded
    assert not b.is_loaded

    swap(None, modulecmd.modes.load, "a", "b")
    assert not a.is_loaded
    assert b.is_loaded


def test_callback_is_loaded(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write("")
    tmpdir.join("b.py").write(
        'if is_loaded("fake"):\n'
        "    stop()\n"
        'if is_loaded("a"):\n'
        '    raise ValueError("a loaded!")\n'
    )
    mock_modulepath(tmpdir.strpath)
    modulecmd.system.load("a")
    with pytest.raises(ValueError):
        modulecmd.system.load("b")


def test_callback_modulepath_ops(tmpdir, mock_modulepath):
    one = tmpdir.mkdir("1")
    one.join("a.py").write("")
    one.join("x.py").write("")
    two = tmpdir.mkdir("2")
    two.join("a.py").write("")

    mock_modulepath(one.strpath)
    x = modulecmd.modulepath.get("x")  # just to set `unlocks`
    a = modulecmd.modulepath.get("a")
    assert a.filename == os.path.join(one.strpath, "a.py")

    append_path = get_callback("append_path")
    append_path(x, modulecmd.modes.load, modulecmd.names.modulepath, two.strpath)
    a = modulecmd.modulepath.get("a")
    assert a.filename == os.path.join(one.strpath, "a.py")
    assert x.unlocks(two.strpath)

    remove_path = get_callback("remove_path")
    remove_path(x, modulecmd.modes.load, modulecmd.names.modulepath, two.strpath)
    a = modulecmd.modulepath.get("a")
    assert a.filename == os.path.join(one.strpath, "a.py")

    prepend_path = get_callback("prepend_path")
    prepend_path(x, modulecmd.modes.load, modulecmd.names.modulepath, two.strpath)
    a = modulecmd.modulepath.get("a")
    assert a.filename == os.path.join(two.strpath, "a.py")
    assert x.unlocks(two.strpath)


def test_callback_stop(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write('setenv("a", "baz")\n' "stop()\n" 'setenv("b", "foo")\n')
    mock_modulepath(tmpdir.strpath)
    modulecmd.system.load("a")
    assert modulecmd.environ.get("a") == "baz"
    assert modulecmd.environ.get("b") is None


def test_callback_setenv():
    setenv = get_callback("setenv")
    unsetenv = get_callback("unsetenv")

    setenv(None, modulecmd.modes.load, "foo", "bar")
    assert modulecmd.environ.environ["foo"] == "bar"
    setenv(None, modulecmd.modes.unload, "foo", "bar")
    assert modulecmd.environ.environ["foo"] is None

    setenv(None, modulecmd.modes.load, "foo", "bar")
    assert modulecmd.environ.environ["foo"] == "bar"
    unsetenv(None, modulecmd.modes.load, "foo")
    assert modulecmd.environ.environ["foo"] is None

    setenv(None, modulecmd.modes.load, "foo", "bar")
    assert modulecmd.environ.environ["foo"] == "bar"
    unsetenv(None, modulecmd.modes.unload, "foo")
    assert modulecmd.environ.environ["foo"] == "bar"


def test_callback_family(tmpdir, mock_modulepath):
    family = get_callback("family")
    tmpdir.mkdir("ucc").join("1.2.py").write("")
    mock_modulepath(tmpdir.strpath)
    module = modulecmd.modulepath.get("ucc")
    family_name = "compiler"
    family(module, modulecmd.modes.load, family_name)
    assert modulecmd.environ.environ["MODULE_FAMILY_COMPILER"] == "ucc"
    assert modulecmd.environ.environ["MODULE_FAMILY_COMPILER_VERSION"] == "1.2"

    family(module, modulecmd.modes.unload, family_name)
    assert modulecmd.environ.environ["MODULE_FAMILY_COMPILER"] is None
    assert modulecmd.environ.environ["MODULE_FAMILY_COMPILER_VERSION"] is None

    modulecmd.environ.environ["MODULE_FAMILY_COMPILER"] = "ucc"
    modulecmd.environ.environ["MODULE_FAMILY_COMPILER_VERSION"] = "2.0"
    with pytest.raises(modulecmd.error.FamilyLoadedError):
        family(module, modulecmd.modes.load, family_name)


def test_callback_help(tmpdir, mock_modulepath):
    help = get_callback("help")
    tmpdir.join("a.py").write("")
    mock_modulepath(tmpdir.strpath)
    a = modulecmd.modulepath.get("a")
    helpstr = "a help string"
    help(a, modulecmd.modes.load, helpstr)
    assert a.helpstr == helpstr


def test_callback_whatis(tmpdir, mock_modulepath):
    whatis = get_callback("whatis")
    tmpdir.join("a.py").write("")
    tmpdir.join("b").write("#%Module1.0")
    mock_modulepath(tmpdir.strpath)
    a = modulecmd.modulepath.get("a")
    whatis_str = "a whatis string"
    whatis(a, modulecmd.modes.load, whatis_str)
    assert a.whatisstr.strip() == whatis_str.strip()
    whatis(
        a,
        modulecmd.modes.load,
        name="foo",
        version="x",
        short_description="a short description",
        foo_bar="baz",
    )
    expected = sorted(
        [
            "name:",
            "foo",
            "version:",
            "x",
            "foo bar:",
            "baz",
            "short description:",
            "a short description",
        ]
    )
    actual = [x.strip() for x in a.whatisstr.split("\n") if x.split()]

    b = modulecmd.modulepath.get("b")
    whatis(b, modulecmd.modes.load, whatis_str)
    assert b.whatisstr.strip() == whatis_str.strip()
    with pytest.raises(ValueError):
        whatis(b, modulecmd.modes.load, whatis_str, whatis_str, whatis_str)


def test_callback_use(tmpdir, mock_modulepath):
    use = get_callback("use")
    unuse = get_callback("unuse")
    one = tmpdir.mkdir("1")
    one.join("x.py").write("")
    one.join("a.py").write("")
    one.join("b.py").write("")
    two = tmpdir.mkdir("2")
    two.join("a.py").write("")
    two.join("b.py").write("")
    mock_modulepath(one.strpath)

    x = modulecmd.modulepath.get("x")
    a = modulecmd.modulepath.get("a")
    assert a.modulepath == one.strpath
    b = modulecmd.modulepath.get("b")
    assert b.modulepath == one.strpath

    use(x, modulecmd.modes.load, two.strpath, append=True)
    assert x.unlocks(two.strpath)
    assert modulecmd.modulepath.contains(two.strpath)
    a = modulecmd.modulepath.get("a")
    assert a.modulepath == one.strpath
    b = modulecmd.modulepath.get("b")
    assert b.modulepath == one.strpath

    use(x, modulecmd.modes.unload, two.strpath, append=True)
    assert x.unlocks(two.strpath)
    assert not modulecmd.modulepath.contains(two.strpath)
    a = modulecmd.modulepath.get("a")
    assert a.modulepath == one.strpath
    b = modulecmd.modulepath.get("b")
    assert b.modulepath == one.strpath

    use(x, modulecmd.modes.load, two.strpath)
    assert x.unlocks(two.strpath)
    assert modulecmd.modulepath.contains(two.strpath)
    a = modulecmd.modulepath.get("a")
    assert a.modulepath == two.strpath
    b = modulecmd.modulepath.get("b")
    assert b.modulepath == two.strpath

    unuse(x, modulecmd.modes.load, two.strpath)
    assert not modulecmd.modulepath.contains(two.strpath)
    a = modulecmd.modulepath.get("a")
    assert a.modulepath == one.strpath
    b = modulecmd.modulepath.get("b")
    assert b.modulepath == one.strpath


def test_callback_get_family_info(tmpdir, mock_modulepath):
    load = get_callback("load")

    a = tmpdir.mkdir("a")
    a.join("1.0.py").write('family("spam")')
    tmpdir.join("b.py").write(
        'x, v = get_family_info("spam")\n' 'assert x == "a"\n' 'assert v == "1.0"'
    )
    mock_modulepath(tmpdir.strpath)
    a = modulecmd.system.load("a")
    assert a.version == "1.0"
    modulecmd.system.load("b")


def test_callback_getenv(tmpdir, mock_modulepath):
    getenv = get_callback("getenv")
    tmpdir.join("a.py").write(
        'setenv("spam", "foo")\n' 'x = getenv("spam")\n' 'assert x == "foo"\n'
    )
    mock_modulepath(tmpdir.strpath)
    a = modulecmd.system.load("a")
    x = getenv(a, modulecmd.modes.load, "spam")
    assert x == "foo"


def test_callback_is_used(tmpdir, mock_modulepath):
    is_used = get_callback("is_used")
    use = get_callback("use")
    one = tmpdir.mkdir("1")
    one.join("a.py").write("")
    two = tmpdir.mkdir("2")
    two.join("b.py").write("")
    mock_modulepath(one.strpath)

    assert is_used(None, modulecmd.modes.load, one.strpath)
    assert not is_used(None, modulecmd.modes.load, two.strpath)

    a = modulecmd.modulepath.get("a")
    use(a, modulecmd.modes.load, two.strpath)
    assert is_used(None, modulecmd.modes.load, one.strpath)
    assert is_used(None, modulecmd.modes.load, two.strpath)


def test_callback_raw(tmpdir, capsys):
    baz = tmpdir.join("baz")
    raw = get_callback("raw")
    raw(None, modulecmd.modes.load, "echo 'BAZ'")
    assert len(modulecmd.environ.environ.raw_shell_commands) == 1
    assert modulecmd.environ.environ.raw_shell_commands[0] == "echo 'BAZ'"
