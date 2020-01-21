import os
import pytest
import pymod.mc
import pymod.alias
from pymod.main import PymodCommand
from pymod.error import ModuleNotFoundError


def test_command_alias(tmpdir, mock_modulepath):
    a = tmpdir.join("a.py").write("")
    mock_modulepath(tmpdir.strpath)
    alias = PymodCommand("alias")
    alias("save", "a", "a-alias")
    a = pymod.mc.load("a-alias")
    aa = pymod.modulepath.get("a")
    assert a.filename == aa.filename

    alias("avail")
    alias("remove", "a-alias")
    assert pymod.alias.get("a-alias") is None

    with pytest.raises(ModuleNotFoundError):
        alias("save", "b", "b-alias")
