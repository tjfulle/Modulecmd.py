import pytest

import modulecmd.system
import modulecmd.error
import modulecmd.environ


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


def test_mc_purge(modules_path, mock_modulepath):
    mock_modulepath(modules_path.path)
    a = modulecmd.system.load("a")
    b = modulecmd.system.load("b")
    c = modulecmd.system.load("c")
    d = modulecmd.system.load("d")
    assert a.is_loaded
    assert b.is_loaded
    assert c.is_loaded
    assert d.is_loaded
    modulecmd.system.purge()
    assert not a.is_loaded
    assert not b.is_loaded
    assert not c.is_loaded
    assert not d.is_loaded


def test_mc_purge_load_after(modules_path, mock_modulepath):
    modulecmd.config.set("load_after_purge", ["a", "b"])
    mock_modulepath(modules_path.path)
    a = modulecmd.system.load("a")
    b = modulecmd.system.load("b")
    c = modulecmd.system.load("c")
    d = modulecmd.system.load("d")
    assert a.is_loaded
    assert b.is_loaded
    assert c.is_loaded
    assert d.is_loaded
    modulecmd.system.purge()
    assert a.is_loaded
    assert b.is_loaded
    assert not c.is_loaded
    assert not d.is_loaded
    modulecmd.config.set("load_after_purge", [])
