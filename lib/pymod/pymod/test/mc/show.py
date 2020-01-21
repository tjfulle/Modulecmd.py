import pytest

import pymod.mc
from pymod.error import ModuleNotFoundError


def test_mc_show(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write('add_option("x")\n' 'setenv("a", "a")')
    mock_modulepath(tmpdir.strpath)

    pymod.mc.show("a")
    pymod.mc.show("a", opts={"x": True})
    with pytest.raises(ModuleNotFoundError):
        pymod.mc.show("fake")


def test_mc_show_tcl(tmpdir, mock_modulepath):
    tmpdir.join("a").write("#%Module1.0")
    mock_modulepath(tmpdir.strpath)
    pymod.mc.show("a")


def test_mc_show_with_error(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write('log_error("spam")')
    mock_modulepath(tmpdir.strpath)
    try:
        pymod.mc.show("a")
        assert False, "Should have died"
    except:
        pass
