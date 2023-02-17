import pytest

import modulecmd.system
import modulecmd.environ
from modulecmd.main import PymodCommand


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds
    one = tmpdir.mkdir("1")
    one.join("a.py").write(m.setenv("a"))
    one.join("b.py").write(m.setenv("b") + m.load("c"))
    one.join("c.py").write(m.setenv("c") + m.load("d"))
    one.join("d.py").write(m.setenv("d") + m.load("e"))
    one.join("e.py").write(m.setenv("e"))
    two = tmpdir.mkdir("2")
    two.join("a.py").write(m.setenv("a"))
    two.join("b.py").write(m.setenv("b") + m.load_first("c", "e", "d"))
    two.join("d.py").write(m.setenv("d"))
    two.join("g.py").write(m.setenv("b") + m.load_first("x", "y", "z", None))
    ns = namespace()
    ns.one = one.strpath
    ns.two = two.strpath
    return ns


def test_command_load_1(modules_path, mock_modulepath):
    load = PymodCommand("load")
    unload = PymodCommand("unload")
    mock_modulepath(modules_path.one)
    load("a")
    assert modulecmd.environ.get("a") == "a"
    unload("a")
    assert modulecmd.environ.get("a") is None


def test_command_load_2(modules_path, mock_modulepath):
    """Load a and b, b loads c, d, e. Then, unload b (c, d, e should also
    unload)
    """
    load = PymodCommand("load")
    unload = PymodCommand("unload")
    mock_modulepath(modules_path.one)
    load("a")
    assert modulecmd.environ.get("a") == "a"

    load("b")
    for x in "bcde":
        assert modulecmd.environ.get(x) == x
        assert modulecmd.system.module_is_loaded(x)

    # just unload e
    unload("d")
    assert modulecmd.environ.get("d") is None
    assert modulecmd.environ.get("e") is None

    # unload b, c and d also unload
    unload("b")
    assert modulecmd.environ.get("b") is None
    assert modulecmd.environ.get("c") is None
    assert modulecmd.environ.get("d") is None
    assert modulecmd.environ.get("a") == "a"

    unload("a")
    assert modulecmd.environ.get("a") is None


def test_command_load_3(modules_path, mock_modulepath):
    """Load a and b, b loads d. Then, unload b (d should also unload)"""
    load = PymodCommand("load")
    unload = PymodCommand("unload")
    mock_modulepath(modules_path.two)

    load("a")
    assert modulecmd.environ.get("a") == "a"

    load("b")
    for x in "ced":
        if x in "ce":
            assert modulecmd.environ.get(x) is None
            assert not modulecmd.system.module_is_loaded(x)
        else:
            assert modulecmd.environ.get(x) == x
            assert modulecmd.system.module_is_loaded(x)

    # unload b, e will also unload
    unload("b")
    assert modulecmd.environ.get("b") is None
    assert modulecmd.environ.get("c") is None
    assert modulecmd.environ.get("d") is None
    assert modulecmd.environ.get("e") is None
    assert modulecmd.environ.get("a") == "a"

    unload("a")
    assert modulecmd.environ.get("a") is None


def test_command_load_collection(tmpdir, mock_modulepath):
    save = PymodCommand("save")
    load = PymodCommand("load")
    purge = PymodCommand("purge")
    restore = PymodCommand("restore")

    tmpdir.join("a.py").write("")
    tmpdir.join("b.py").write("")
    tmpdir.join("c.py").write("")
    tmpdir.join("d.py").write("")
    mock_modulepath(tmpdir.strpath)
    a = load("a")
    b = load("b")
    c = load("c")
    d = load("d")
    save("foo")
    purge()
    restore("foo")

    for x in "abcd":
        m = modulecmd.modulepath.get(x)
        assert m.is_loaded
    purge()
    for x in "abcd":
        m = modulecmd.modulepath.get(x)
        assert not m.is_loaded
    load("foo")
    for x in "abcd":
        m = modulecmd.modulepath.get(x)
        assert m.is_loaded
