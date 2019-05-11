import os
import pytest

import pymod.mc
import pymod.error
import pymod.environ


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds
    tmpdir.join('a.py').write(m.setenv('module_swap', 'a'))
    tmpdir.join('b.py').write(m.setenv('module_swap', 'b'))
    tmpdir.join('c.py').write(m.swap('a', 'b'))
    tmpdir.join('d.py').write(m.swap('a', 'spam'))
    tmpdir.join('e.py').write(m.swap('spam', 'a'))
    tmpdir.join('f.py').write(m.swap('a', 'b'))
    ns = namespace()
    ns.path = tmpdir.strpath
    return ns


@pytest.mark.unit
def test_mc_swap_1(modules_path, mock_modulepath):
    mp = mock_modulepath(modules_path.path)
    pymod.mc.load('a')
    assert pymod.environ.get('module_swap') == 'a'
    pymod.mc.swap('a', 'b')
    assert pymod.environ.get('module_swap') == 'b'


def test_mc_swap_2(modules_path, mock_modulepath):
    mp = mock_modulepath(modules_path.path)
    a = pymod.mc.load('a')
    assert a.is_loaded
    assert pymod.environ.get('module_swap') == 'a'
    c = pymod.mc.load('c')
    b = pymod.modulepath.get('b')
    assert pymod.environ.get('module_swap') == 'b'
    assert c.is_loaded
    assert b.is_loaded
    assert not a.is_loaded

    # Module b is loaded, nothing to do
    pymod.mc.load('f')
    assert pymod.environ.get('module_swap') == 'b'
    pymod.mc.unload('f')
    pymod.mc.unload('c')

    # Unload b and then load c.  a is not loaded, but b should still be
    pymod.mc.unload('b')
    assert pymod.environ.get('module_swap') is None
    pymod.mc.load('c')
    assert pymod.environ.get('module_swap') == 'b'


def test_mc_swap_3(modules_path, mock_modulepath):
    mp = mock_modulepath(modules_path.path)
    pymod.mc.load('a')
    with pytest.raises(pymod.error.ModuleNotFoundError):
        pymod.mc.load('d')
    with pytest.raises(pymod.error.ModuleNotFoundError):
        pymod.mc.load('e')
    pymod.mc.load('c')
    assert pymod.environ.get('module_swap') == 'b'
