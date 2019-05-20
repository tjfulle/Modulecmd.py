import pytest

import pymod.mc
from pymod.error import ModuleNotFoundError


def test_mc_help(tmpdir, modulecmds, mock_modulepath):
    m = modulecmds
    tmpdir.join('a.py').write(m.help('HELP A'))
    mock_modulepath(tmpdir.strpath)
    pymod.mc.help('a')

    with pytest.raises(ModuleNotFoundError):
        pymod.mc.help('b')
