import os
import pytest

import pymod.mc
import pymod.error
import pymod.environ


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds
    tmpdir.join('a.py').write(m.setenv('a'))
    tmpdir.join('a1.py').write(m.setenv('a1')+m.load('a'))
    tmpdir.join('a2.py').write(m.setenv('a2')+m.load('a'))
    tmpdir.join('b.py').write(m.setenv('b')+m.unload('a'))
    ns = namespace()
    ns.path = tmpdir.strpath
    return ns


def test_mc_unload_1(modules_path, mock_modulepath):
    mp = mock_modulepath(modules_path.path)
    a = pymod.mc.load('a')
    assert pymod.environ.get('a') == 'a'
    assert a.is_loaded
    pymod.mc.unload('a')
    assert pymod.environ.get('a') is None
    assert not a.is_loaded


def test_mc_unload_2(modules_path, mock_modulepath):
    mp = mock_modulepath(modules_path.path)
    a = pymod.mc.load('a')
    assert pymod.environ.get('a') == 'a'
    b = pymod.mc.load('b')
    assert pymod.environ.get('b') == 'b'
    assert pymod.environ.get('a') is None
    assert not a.is_loaded
    assert b.is_loaded


def test_mc_unload_3(modules_path, mock_modulepath):
    mp = mock_modulepath(modules_path.path)
    a = pymod.mc.load('a')
    a1 = pymod.mc.load('a1')
    a2 = pymod.mc.load('a2')
    assert pymod.environ.get('a') == 'a'
    assert pymod.environ.get('a1') == 'a1'
    assert pymod.environ.get('a2') == 'a2'

    # a was "loaded" 3  times, loading b causes the
    pymod.mc.unload('a2')
    assert a.is_loaded
    pymod.mc.unload('a1')
    assert a.is_loaded
    pymod.mc.unload('a')
    assert not a.is_loaded


def test_mc_unload_bad(modules_path, mock_modulepath):
    mp = mock_modulepath(modules_path.path)
    a = pymod.modulepath.get('a')
    assert not a.is_loaded
    with pytest.raises(pymod.error.ModuleNotLoadedError):
        pymod.mc.unload_impl(a)


def test_mc_unload_right_version(tmpdir, mock_modulepath):
    a = tmpdir.mkdir('a')
    a.join('1.0.py').write('')
    a.join('2.0.py').write('')
    mp = mock_modulepath(tmpdir.strpath)
    a = pymod.mc.load('a/1.0')
    # This will unload `a` by name, even though the version 1.0 is not the default
    pymod.mc.unload('a')
    assert not a.is_loaded
