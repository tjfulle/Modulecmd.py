import pytest

import modulecmd.system
from modulecmd.error import ModuleNotFoundError


def test_mc_help(tmpdir, modulecmds, mock_modulepath):
    m = modulecmds
    tmpdir.join("a.py").write(m.help("HELP A"))
    mock_modulepath(tmpdir.strpath)
    modulecmd.system.help("a")

    with pytest.raises(ModuleNotFoundError):
        modulecmd.system.help("b")
