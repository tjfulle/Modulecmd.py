import pytest

import modulecmd.system
import modulecmd.modulepath
from modulecmd.main import PymodCommand


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds
    one = tmpdir.mkdir("1")
    one.join("a.py").write(m.setenv("a"))
    one.join("b.py").write(m.setenv("b"))
    two = tmpdir.mkdir("2")
    two.join("c.py").write(m.setenv("c"))
    two.join("d.py").write(m.setenv("d"))
    ns = namespace()
    ns.one = one.strpath
    ns.two = two.strpath
    return ns


@pytest.mark.unit
def test_command_unuse(modules_path, mock_modulepath):
    unuse = PymodCommand("unuse")
    load = PymodCommand("load")

    mock_modulepath([modules_path.one, modules_path.two])
    a = modulecmd.system.load("a")
    b = modulecmd.system.load("b")
    unuse(modules_path.one)

    c = modulecmd.system.load("c")
    d = modulecmd.system.load("d")
    unuse(modules_path.two)

    loaded = modulecmd.system.loaded_modules()
    assert len(loaded) == 0

    assert modulecmd.modulepath.size() == 0
