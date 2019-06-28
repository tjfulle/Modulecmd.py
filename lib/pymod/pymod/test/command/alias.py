import os
import pytest
import pymod.mc
from pymod.main import PymodCommand


def test_command_alias(tmpdir, mock_modulepath):
    a = tmpdir.join('a.py').write('')
    mock_modulepath(tmpdir.strpath)
    alias = PymodCommand('alias')
    alias('a', 'a-alias')
    a = pymod.mc.load('a-alias')
    aa = pymod.modulepath.get('a')
    assert a.filename == aa.filename
