import os
import pytest

import modulecmd.system
import modulecmd.error
import modulecmd.modes
import modulecmd.environ

"""Test module callback functions by actually executing the module"""


def test_mc_execmodule_path_ops(tmpdir, modulecmds, mock_modulepath):
    m = modulecmds
    tmpdir.join("a.py").write(
        m.append_path("foo", "bar", sep=":") + m.prepend_path("foo", "baz", sep=":")
    )
    tmpdir.join("b.py").write(m.remove_path("foo", "baz") + m.remove_path("foo", "bar"))
    tmpdir.join("c.py").write(
        m.append_path("spam", "ham", sep=";") + m.prepend_path("spam", "eggs", sep=";")
    )
    tmpdir.join("d.py").write(
        m.remove_path("spam", "ham", sep=";") + m.remove_path("spam", "eggs", sep=";")
    )
    mock_modulepath(tmpdir.strpath)

    c = modulecmd.system.load("c")
    assert modulecmd.environ.get("spam") == "eggs;ham"
    d = modulecmd.system.load("d")
    assert modulecmd.environ.get("spam") is None

    modulecmd.system.load("a")
    assert modulecmd.environ.get("foo") == "baz:bar"
    modulecmd.system.load("b")
    assert modulecmd.environ.get("foo") is None

    c = modulecmd.system.unload("b")
    c = modulecmd.system.unload("a")
    c = modulecmd.system.unload("d")
    c = modulecmd.system.unload("c")


def test_mc_execmodule_conflict(tmpdir, modulecmds, mock_modulepath):
    m = modulecmds
    tmpdir.join("a.py").write(m.setenv("a") + m.setenv("__x__") + m.unsetenv("__x__"))
    tmpdir.join("b.py").write(m.conflict("a"))
    mock_modulepath(tmpdir.strpath)
    a = modulecmd.system.load("a")
    with pytest.raises(modulecmd.error.ModuleConflictError):
        b = modulecmd.system.load("b")


def test_mc_execmodule_prereq(tmpdir, modulecmds, mock_modulepath):
    m = modulecmds
    tmpdir.join("a.py").write(m.setenv("a"))
    tmpdir.join("b.py").write(m.prereq("a"))
    tmpdir.join("c.py").write(m.prereq_any("x", "y", "b"))
    mock_modulepath(tmpdir.strpath)
    a = modulecmd.system.load("a")
    # no problem, prereq a is loaded
    b = modulecmd.system.load("b")

    modulecmd.system.unload("b")
    modulecmd.system.unload("a")

    # If we unload a, b will error out
    with pytest.raises(modulecmd.error.PrereqMissingError):
        modulecmd.system.load("b")

    modulecmd.system.unload("b")
    modulecmd.system.unload("a")

    with pytest.raises(modulecmd.error.PrereqMissingError):
        modulecmd.system.load("c")

    modulecmd.system.load("a")
    modulecmd.system.load("b")
    modulecmd.system.load("c")


def test_mc_execmodule_set_alias(tmpdir, modulecmds, mock_modulepath):
    m = modulecmds
    tmpdir.join("a.py").write(m.set_alias("foo", "bar"))
    tmpdir.join("b.py").write(m.unset_alias("foo"))
    mock_modulepath(tmpdir.strpath)
    a = modulecmd.system.load("a")
    assert modulecmd.environ.environ.aliases["foo"] == "bar"
    b = modulecmd.system.load("b")
    assert modulecmd.environ.environ.aliases["foo"] is None
    modulecmd.system.unload("a")
    a = modulecmd.system.load("a")
    assert modulecmd.environ.environ.aliases["foo"] == "bar"
    modulecmd.system.unload("a")
    assert modulecmd.environ.environ.aliases["foo"] is None


def test_mc_execmodule_set_shell_function(tmpdir, modulecmds, mock_modulepath):
    m = modulecmds
    tmpdir.join("a.py").write(m.set_shell_function("baz", "bar $@"))
    tmpdir.join("b.py").write(m.unset_shell_function("baz"))
    mock_modulepath(tmpdir.strpath)
    a = modulecmd.system.load("a")
    assert modulecmd.environ.environ.shell_functions["baz"] == "bar $@"
    b = modulecmd.system.load("b")
    assert modulecmd.environ.environ.shell_functions["baz"] is None
    modulecmd.system.unload("a")
    a = modulecmd.system.load("a")
    assert modulecmd.environ.environ.shell_functions["baz"] == "bar $@"
    modulecmd.system.unload("a")
    assert modulecmd.environ.environ.shell_functions["baz"] is None


def test_mc_execmodule_source(tmpdir, modulecmds, mock_modulepath, capsys):
    m = modulecmds
    baz = tmpdir.join("baz")
    baz.write("echo BAZ")
    tmpdir.join("a.py").write(m.source(baz.strpath))
    mock_modulepath(tmpdir.strpath)
    a = modulecmd.system.load("a")
    assert modulecmd.environ.environ.files_to_source[0][0] == baz.strpath
    modulecmd.environ.environ.files_to_source = []


def test_mc_execmodule_load_first(tmpdir, mock_modulepath):
    mock_modulepath(tmpdir.strpath)
    load_first = modulecmd.callback.get_callback("load_first")
    with pytest.raises(modulecmd.error.ModuleNotFoundError):
        load_first(None, modulecmd.modes.load, "x", "y", "z")
    load_first(None, modulecmd.modes.load, "x", "y", "z", None)


def test_mc_execmodule_is_loaded(tmpdir, mock_modulepath):
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


def test_mc_execmodule_modulepath_ops(tmpdir, mock_modulepath):
    one = tmpdir.mkdir("1")
    one.join("a.py").write("")
    two = tmpdir.mkdir("2")
    two.join("a.py").write("")
    core = tmpdir.mkdir("core")
    x = core.mkdir("x")
    f1 = x.join("1.py").write(
        "append_path({0!r}, {1!r})".format(modulecmd.names.modulepath, one.strpath)
    )
    f2 = x.join("2.py").write(
        "prepend_path({0!r}, {1!r})".format(modulecmd.names.modulepath, two.strpath)
    )
    mock_modulepath(core.strpath)

    x = modulecmd.system.load("x/1")
    a = modulecmd.modulepath.get("a")
    assert a.file == os.path.join(one.strpath, "a.py")
    assert x.unlocks(one.strpath)

    x = modulecmd.system.load("x/2")
    a = modulecmd.modulepath.get("a")
    assert a.file == os.path.join(two.strpath, "a.py")
    assert x.unlocks(two.strpath)


def test_mc_execmodule_stop(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write('setenv("a", "baz")\n' "stop()\n" 'setenv("b", "foo")\n')
    mock_modulepath(tmpdir.strpath)
    modulecmd.system.load("a")
    assert modulecmd.environ.get("a") == "baz"
    assert modulecmd.environ.get("b") is None
