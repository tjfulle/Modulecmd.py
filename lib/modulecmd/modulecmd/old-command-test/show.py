import pytest
from modulecmd.main import PymodCommand
from modulecmd.error import ModuleNotFoundError


def test_command_show(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write('append_path("FOO", "/a/b/c", sep=";")')
    show = PymodCommand("show")
    mock_modulepath(tmpdir.strpath)
    show("a", "+x")
    with pytest.raises(ModuleNotFoundError):
        show("fake")
    with pytest.raises(ValueError):
        # need module for options
        show("+x")
