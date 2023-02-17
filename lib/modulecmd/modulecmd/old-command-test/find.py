import pytest
import modulecmd.error
from modulecmd.main import PymodCommand


def test_command_find(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write("")
    find = PymodCommand("find")
    mock_modulepath(tmpdir.strpath)
    find("a")
    with pytest.raises(modulecmd.error.ModuleNotFoundError):
        find("b")
