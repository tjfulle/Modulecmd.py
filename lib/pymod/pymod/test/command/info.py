import pytest
import pymod.mc
from pymod.main import PymodCommand
def test_command_info(tmpdir, mock_modulepath):
    tmpdir.join('a.py').write('')
    info = PymodCommand('info')
    mock_modulepath(tmpdir.strpath)
    pymod.mc.load('a')
    info('a')
    pymod.mc.unload('a')
    # Error is raised because a is not loaded
    with pytest.raises(ValueError):
        info('a')
    # Even though module does not exist, a value is raised because `info` only
    # looks through loaded modules and not all possible modules
    with pytest.raises(ValueError):
        info('b')
