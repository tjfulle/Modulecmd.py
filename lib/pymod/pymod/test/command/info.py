import pytest
import pymod.mc
import pymod.error
from pymod.main import PymodCommand


def test_command_info(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write("")
    info = PymodCommand("info")
    mock_modulepath(tmpdir.strpath)
    info("a")
    with pytest.raises(pymod.error.ModuleNotFoundError):
        info("b")
