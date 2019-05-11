import pytest

import pymod.mc
from pymod.error import ModuleNotFoundError


def test_mc_whatis(tmpdir, modulecmds, mock_modulepath):
    m = modulecmds
    tmpdir.join('a.py').write(m.whatis('WHATIS A'))
    mp = mock_modulepath(tmpdir.strpath)
    pymod.mc.whatis('a')

    with pytest.raises(ModuleNotFoundError):
        pymod.mc.whatis('b')
