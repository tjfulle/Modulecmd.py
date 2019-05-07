import os
import pytest

import pymod.mc
import pymod.error
import pymod.environ


@pytest.fixture()
def modules_path(tmpdir):
    tmpdir.join('a.py').write("setenv('MODULE_SWAP', 'a')")
    tmpdir.join('b.py').write("setenv('MODULE_SWAP', 'b')")
    tmpdir.join('c.py').write("swap('a', 'b')")
    tmpdir.join('d.py').write("swap('a', 'spam')")
    tmpdir.join('e.py').write("swap('spam', 'a')")
    tmpdir.join('f.py').write("swap('a', 'b')")
    return tmpdir.strpath


@pytest.mark.unit
def test_swap_1(modules_path, mock_modulepath):
    mp = mock_modulepath(modules_path)
    pymod.mc.load('a')
    pymod.environ.get('MODULE_SWAP') == 'a'
    pymod.mc.swap('a', 'b')
    pymod.environ.get('MODULE_SWAP') == 'b'

def test_swap_2(modules_path, mock_modulepath):
    mp = mock_modulepath(modules_path)
    pymod.mc.load('a')
    assert pymod.environ.get('MODULE_SWAP') == 'a'
    pymod.mc.load('c')
    assert pymod.environ.get('MODULE_SWAP') == 'b'

    # Module b is loaded, nothing to do
    pymod.mc.load('c')
    assert pymod.environ.get('MODULE_SWAP') == 'b'

    # Unload b and then load c.  a is not loaded, but b should still be
    pymod.mc.unload('c')
    pymod.mc.unload('b')
    assert pymod.environ.get('MODULE_SWAP') is None
    pymod.mc.load('c')
    assert pymod.environ.get('MODULE_SWAP') == 'b'

def test_swap_3(modules_path, mock_modulepath):
    mp = mock_modulepath(modules_path)
    pymod.mc.load('a')
    with pytest.raises(pymod.error.ModuleNotFoundError):
        pymod.mc.load('d')
    with pytest.raises(pymod.error.ModuleNotFoundError):
        pymod.mc.load('e')
    pymod.mc.load('f')
    assert pymod.environ.get('MODULE_SWAP') == 'b'
