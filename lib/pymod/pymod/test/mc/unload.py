import os
import pytest

import pymod.mc
import pymod.error
import pymod.environ


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds
    tmpdir.mkdir('1')
    tmpdir.join('a.py').write(m.setenv('a'))
    tmpdir.join('a2.py').write(m.setenv('a2')+m.load('a'))
    tmpdir.join('a3.py').write(m.setenv('a3')+m.load('a'))
    tmpdir.join('b.py').write(m.setenv('b')+m.unload('a'))
    ns = namespace()
    ns.path = tmpdir.strpath
    return ns


@pytest.mark.unit
def test_unload_1(modules_path, mock_modulepath):
    """Just load and then unload a"""
    mp = mock_modulepath(modules_path.path)
    a = pymod.mc.load('a')
    assert pymod.environ.get('__a__') == '__a__'
    assert a.is_loaded
    pymod.mc.unload('a')
    assert pymod.environ.get('__a__') is None
    assert not a.is_loaded


@pytest.mark.unit
def test_unload_2(modules_path, mock_modulepath):
    """Just load and then unload a"""
    mp = mock_modulepath(modules_path.path)
    a = pymod.mc.load('a')
    assert pymod.environ.get('__a__') == '__a__'
    b = pymod.mc.load('b')
    assert pymod.environ.get('__b__') == '__b__'
    assert pymod.environ.get('__a__') is None
    assert not a.is_loaded
    assert b.is_loaded


@pytest.mark.unit
def test_unload_3(modules_path, mock_modulepath):
    """Just load and then unload a"""
    mp = mock_modulepath(modules_path.path)
    a = pymod.mc.load('a')
    a2 = pymod.mc.load('a2')
    a3 = pymod.mc.load('a3')
    assert pymod.environ.get('__a__') == '__a__'
    assert pymod.environ.get('__a2__') == '__a2__'
    assert pymod.environ.get('__a3__') == '__a3__'

    # a was "loaded" 3  times, loading b causes the
    pymod.mc.unload('a3')
    assert a.is_loaded
    pymod.mc.unload('a2')
    assert a.is_loaded
    pymod.mc.unload('a')
    assert not a.is_loaded
