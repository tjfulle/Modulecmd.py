import os
import pytest
import modulecmd.system
import modulecmd.alias
from modulecmd.main import PymodCommand
from modulecmd.error import ModuleNotFoundError


def test_command_alias(tmpdir, mock_modulepath):
    a = tmpdir.join("a.py").write("")
    mock_modulepath(tmpdir.strpath)
    alias = PymodCommand("alias")
    alias("save", "a", "a-alias")
    a = modulecmd.system.load("a-alias")
    aa = modulecmd.modulepath.get("a")
    assert a.filename == aa.filename

    alias("avail")
    alias("remove", "a-alias")
    assert modulecmd.alias.get("a-alias") is None

    with pytest.raises(ModuleNotFoundError):
        alias("save", "b", "b-alias")
