import os
import pytest

import pymod.mc
import pymod.environ
from pymod.error import ModuleNotFoundError


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds
    one = tmpdir.mkdir('1')
    one.join('a.py').write(m.setenv('a'))
    one.join('b.py').write(m.setenv('b')+m.load('c'))
    one.join('c.py').write(m.setenv('c')+m.load('d'))
    one.join('d.py').write(m.setenv('d'))
    ns = namespace()
    ns.path = one.strpath
    return ns


def test_mc_reload_1(modules_path, mock_modulepath):
    mp = mock_modulepath(modules_path.path)
    a = pymod.mc.load('a')
    assert pymod.environ.get('a') == 'a'
    pymod.mc.reload('a')
    assert pymod.environ.get('a') == 'a'
    # Reference count should not change
    assert pymod.mc.get_refcount(a) == 1


def test_mc_reload_2(modules_path, mock_modulepath):
    mp = mock_modulepath(modules_path.path)
    a = pymod.mc.load('a')
    b = pymod.mc.load('b')
    assert a.is_loaded
    assert b.is_loaded
    c = pymod.modulepath.get('c')
    d = pymod.modulepath.get('d')
    assert c.is_loaded
    assert d.is_loaded
    pymod.mc.reload('a')
    assert pymod.environ.get('a') == 'a'
    # Reference count should not change
    assert pymod.mc.get_refcount(a) == 1
    assert pymod.mc.get_refcount(b) == 1


def test_mc_reload_3(modules_path, mock_modulepath):
    mp = mock_modulepath(modules_path.path)
    x = pymod.mc.reload('a')
    assert x is None
    with pytest.raises(ModuleNotFoundError):
        pymod.mc.reload('fake')
