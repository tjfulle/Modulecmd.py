import pytest

import modulecmd.system
import modulecmd.error
import modulecmd.environ
from modulecmd.main import PymodCommand


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds
    tmpdir.join("a.py").write(m.setenv("a"))
    tmpdir.join("a1.py").write(m.setenv("a1") + m.load("a"))
    tmpdir.join("a2.py").write(m.setenv("a2") + m.load("a"))
    tmpdir.join("b.py").write(m.setenv("b") + m.unload("a"))
    ns = namespace()
    ns.path = tmpdir.strpath
    return ns


@pytest.mark.unit
def test_command_unload_1(modules_path, mock_modulepath):
    load = PymodCommand("load")
    unload = PymodCommand("unload")
    mock_modulepath(modules_path.path)
    load("a")
    a = modulecmd.modulepath.get("a")
    assert modulecmd.environ.get("a") == "a"
    assert a.is_loaded
    modulecmd.system.unload("a")
    assert modulecmd.environ.get("a") is None
    assert not a.is_loaded


@pytest.mark.unit
def test_command_unload_2(modules_path, mock_modulepath):
    load = PymodCommand("load")
    unload = PymodCommand("unload")
    mock_modulepath(modules_path.path)
    load("a")
    a = modulecmd.modulepath.get("a")
    assert modulecmd.environ.get("a") == "a"
    load("b")
    b = modulecmd.modulepath.get("b")
    assert modulecmd.environ.get("b") == "b"
    assert modulecmd.environ.get("a") is None
    assert not a.is_loaded
    assert b.is_loaded


@pytest.mark.unit
def test_command_unload_3(modules_path, mock_modulepath):
    load = PymodCommand("load")
    unload = PymodCommand("unload")
    mock_modulepath(modules_path.path)
    load("a")
    load("a1")
    load("a2")
    assert modulecmd.environ.get("a") == "a"
    assert modulecmd.environ.get("a1") == "a1"
    assert modulecmd.environ.get("a2") == "a2"

    # a was "loaded" 3  times, loading b causes the
    unload("a2")
    a = modulecmd.modulepath.get("a")
    assert a.is_loaded
    unload("a1")
    assert a.is_loaded
    unload("a")
    assert not a.is_loaded
