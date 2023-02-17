import pytest

import modulecmd.system
from modulecmd.error import ModuleNotFoundError


def test_mc_whatis(tmpdir, mock_modulepath):
    f = tmpdir.join("a.py")
    f.write("add_option('foo')\n")
    f.write("add_option('bar', help='A bar')\n")
    f.write("whatis('WHATIS A')\n")
    mock_modulepath(tmpdir.strpath)
    modulecmd.system.whatis("a")
    with pytest.raises(ModuleNotFoundError):
        modulecmd.system.whatis("b")
