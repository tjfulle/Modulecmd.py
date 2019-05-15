import pytest
import pymod.error
from pymod.main import PymodCommand
def test_command_find(tmpdir, mock_modulepath):
    tmpdir.join('a.py').write('')
    find = PymodCommand('find')
    mp = mock_modulepath(tmpdir.strpath)
    find('a')
    with pytest.raises(pymod.error.ModuleNotFoundError):
        find('b')
