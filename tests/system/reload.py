import pytest

import modulecmd.system
import modulecmd.environ
from modulecmd.error import ModuleNotFoundError


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds
    one = tmpdir.mkdir("1")
    one.join("a.py").write(m.setenv("a"))
    one.join("b.py").write(m.setenv("b") + m.load("c"))
    one.join("c.py").write(m.setenv("c") + m.load("d"))
    one.join("d.py").write(m.setenv("d"))
    ns = namespace()
    ns.path = one.strpath
    return ns


def test_mc_reload_1(modules_path, mock_modulepath):
    mock_modulepath(modules_path.path)
    a = modulecmd.system.load("a")
    assert modulecmd.environ.get("a") == "a"
    modulecmd.system.reload("a")
    assert modulecmd.environ.get("a") == "a"
    # Reference count should not change
    assert a.refcount == 1


def test_mc_reload_2(modules_path, mock_modulepath):
    mock_modulepath(modules_path.path)
    a = modulecmd.system.load("a")
    b = modulecmd.system.load("b")
    assert a.is_loaded
    assert b.is_loaded
    c = modulecmd.modulepath.get("c")
    d = modulecmd.modulepath.get("d")
    assert c.is_loaded
    assert d.is_loaded
    modulecmd.system.reload("a")
    assert modulecmd.environ.get("a") == "a"
    # Reference count should not change
    assert a.refcount == 1
    assert a.refcount == 1


def test_mc_reload_3(modules_path, mock_modulepath):
    mock_modulepath(modules_path.path)
    x = modulecmd.system.reload("a")
    assert x is None
    with pytest.raises(ModuleNotFoundError):
        modulecmd.system.reload("fake")
