import pytest

from pymod.main import PymodCommand
from pymod.error import ModuleNotFoundError


def test_command_whatis(tmpdir, modulecmds, mock_modulepath):
    m = modulecmds
    tmpdir.join('a.py').write(m.whatis('WHATIS A'))
    mp = mock_modulepath(tmpdir.strpath)
    whatis = PymodCommand('whatis')
    whatis('a')

    with pytest.raises(ModuleNotFoundError):
        whatis('b')
