import pytest
import modulecmd.error
from modulecmd.main import PymodCommand


def test_command_info(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write("")
    info = PymodCommand("info")
    mock_modulepath(tmpdir.strpath)
    info("a")
    with pytest.raises(modulecmd.error.ModuleNotFoundError):
        info("b")
