import pytest

import modulecmd.system
from modulecmd.error import ModuleNotFoundError


def test_mc_show(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write('add_option("x")\n' 'setenv("a", "a")')
    mock_modulepath(tmpdir.strpath)

    modulecmd.system.show("a")
    modulecmd.system.show("a", opts={"x": True})
    with pytest.raises(ModuleNotFoundError):
        modulecmd.system.show("fake")


def test_mc_show_tcl(tmpdir, mock_modulepath):
    tmpdir.join("a").write("#%Module1.0")
    mock_modulepath(tmpdir.strpath)
    modulecmd.system.show("a")


def test_mc_show_with_error(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write('log_error("spam")')
    mock_modulepath(tmpdir.strpath)
    try:
        modulecmd.system.show("a")
        assert False, "Should have died"
    except:
        pass
