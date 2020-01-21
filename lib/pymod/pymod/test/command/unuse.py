import pytest

import pymod.mc
import pymod.modulepath
from pymod.main import PymodCommand


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
    a = pymod.mc.load("a")
    b = pymod.mc.load("b")
    unuse(modules_path.one)

    c = pymod.mc.load("c")
    d = pymod.mc.load("d")
    unuse(modules_path.two)

    loaded = pymod.mc.get_loaded_modules()
    assert len(loaded) == 0

    assert pymod.modulepath.size() == 0
