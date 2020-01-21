import pytest

import pymod.mc
import pymod.error
import pymod.environ


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds
    tmpdir.join("a.py").write(m.setenv("a"))
    tmpdir.join("b.py").write(m.setenv("b"))
    tmpdir.join("c.py").write(m.setenv("c"))
    tmpdir.join("d.py").write(m.setenv("d") + m.load("e"))
    tmpdir.join("e.py").write(m.setenv("d"))
    ns = namespace()
    ns.path = tmpdir.strpath
    return ns


@pytest.mark.unit
def test_mc_purge(modules_path, mock_modulepath):
    mock_modulepath(modules_path.path)
    a = pymod.mc.load("a")
    b = pymod.mc.load("b")
    c = pymod.mc.load("c")
    d = pymod.mc.load("d")
    assert a.is_loaded
    assert b.is_loaded
    assert c.is_loaded
    assert d.is_loaded
    pymod.mc.purge()
    assert not a.is_loaded
    assert not b.is_loaded
    assert not c.is_loaded
    assert not d.is_loaded


@pytest.mark.unit
def test_mc_purge_load_after(modules_path, mock_modulepath):
    pymod.config.set("load_after_purge", ["a", "b"])
    mock_modulepath(modules_path.path)
    a = pymod.mc.load("a")
    b = pymod.mc.load("b")
    c = pymod.mc.load("c")
    d = pymod.mc.load("d")
    assert a.is_loaded
    assert b.is_loaded
    assert c.is_loaded
    assert d.is_loaded
    pymod.mc.purge()
    assert a.is_loaded
    assert b.is_loaded
    assert not c.is_loaded
    assert not d.is_loaded
    pymod.config.set("load_after_purge", [])
