import pytest

import modulecmd.environ
from modulecmd.main import PymodCommand


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


@pytest.mark.unit
def test_command_reload_1(modules_path, mock_modulepath):
    load = PymodCommand("load")
    reload = PymodCommand("reload")
    mock_modulepath(modules_path.path)
    load("a")
    assert modulecmd.environ.get("a") == "a"
    reload("a")
    assert modulecmd.environ.get("a") == "a"
    # Reference count should not change
    a = modulecmd.modulepath.get("a")
    assert a.refcount == 1


@pytest.mark.unit
def test_command_reload_2(modules_path, mock_modulepath):
    load = PymodCommand("load")
    reload = PymodCommand("reload")
    mock_modulepath(modules_path.path)
    load("a")
    load("b")
    assert modulecmd.environ.get("a") == "a"
    assert modulecmd.environ.get("b") == "b"
    assert modulecmd.environ.get("c") == "c"
    assert modulecmd.environ.get("d") == "d"
    reload("a")
    assert modulecmd.environ.get("a") == "a"
    # Reference count should not change
    a = modulecmd.modulepath.get("a")
    b = modulecmd.modulepath.get("b")
    assert a.refcount == 1
    assert b.refcount == 1
