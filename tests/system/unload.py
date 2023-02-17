import pytest

import modulecmd.system
import modulecmd.error
import modulecmd.environ


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds
    tmpdir.join("a.py").write(m.setenv("a"))
    tmpdir.join("a1.py").write(m.setenv("a1") + m.load("a"))
    tmpdir.join("a2.py").write(m.setenv("a2") + m.load("a"))
    tmpdir.join("b.py").write(m.setenv("b") + m.unload("a"))
    x = tmpdir.mkdir("x")
    x.join("1.0.py").write("")
    ns = namespace()
    ns.path = tmpdir.strpath
    return ns


def test_mc_unload_1(modules_path, mock_modulepath):
    mock_modulepath(modules_path.path)
    a = modulecmd.system.load("a")
    assert modulecmd.environ.get("a") == "a"
    assert a.is_loaded
    modulecmd.system.unload("a")
    assert modulecmd.environ.get("a") is None
    assert not a.is_loaded
    x = modulecmd.system.load("x/1.0")
    assert x.is_loaded
    x = modulecmd.system.unload("x/1.0")
    assert not x.is_loaded


def test_mc_unload_2(modules_path, mock_modulepath):
    mock_modulepath(modules_path.path)
    a = modulecmd.system.load("a")
    assert modulecmd.environ.get("a") == "a"
    b = modulecmd.system.load("b")
    assert modulecmd.environ.get("b") == "b"
    assert modulecmd.environ.get("a") is None
    assert not a.is_loaded
    assert b.is_loaded


def test_mc_unload_3(modules_path, mock_modulepath):
    mock_modulepath(modules_path.path)
    a = modulecmd.system.load("a")
    a1 = modulecmd.system.load("a1")
    a2 = modulecmd.system.load("a2")
    assert modulecmd.environ.get("a") == "a"
    assert modulecmd.environ.get("a1") == "a1"
    assert modulecmd.environ.get("a2") == "a2"

    # a was "loaded" 3  times, loading b causes the
    modulecmd.system.unload("a2")
    assert a.is_loaded
    modulecmd.system.unload("a1")
    assert a.is_loaded
    modulecmd.system.unload("a")
    assert not a.is_loaded


def test_mc_unload_bad(modules_path, mock_modulepath):
    mock_modulepath(modules_path.path)
    a = modulecmd.modulepath.get("a")
    assert not a.is_loaded
    with pytest.raises(modulecmd.error.ModuleNotLoadedError):
        modulecmd.system.unload_impl(a)


def test_mc_unload_right_version(tmpdir, mock_modulepath):
    a = tmpdir.mkdir("a")
    a.join("1.0.py").write("")
    a.join("2.0.py").write("")
    mock_modulepath(tmpdir.strpath)
    a = modulecmd.system.load("a/1.0")
    # This will unload `a` by name, even though the version 1.0 is not the default
    modulecmd.system.unload("a")
    assert not a.is_loaded
