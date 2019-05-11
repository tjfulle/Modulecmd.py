import os
import pytest

import pymod.mc
import pymod.error
import pymod.environ
from pymod.main import PymodCommand


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


@pytest.mark.unit
def test_command_unload_1(modules_path, mock_modulepath):
    load = PymodCommand('load')
    unload = PymodCommand('unload')
    mp = mock_modulepath(modules_path.path)
    load('a')
    a = pymod.modulepath.get('a')
    assert pymod.environ.get('a') == 'a'
    assert a.is_loaded
    pymod.mc.unload('a')
    assert pymod.environ.get('a') is None
    assert not a.is_loaded


@pytest.mark.unit
def test_command_unload_2(modules_path, mock_modulepath):
    load = PymodCommand('load')
    unload = PymodCommand('unload')
    mp = mock_modulepath(modules_path.path)
    load('a')
    a = pymod.modulepath.get('a')
    assert pymod.environ.get('a') == 'a'
    load('b')
    b = pymod.modulepath.get('b')
    assert pymod.environ.get('b') == 'b'
    assert pymod.environ.get('a') is None
    assert not a.is_loaded
    assert b.is_loaded


@pytest.mark.unit
def test_command_unload_3(modules_path, mock_modulepath):
    load = PymodCommand('load')
    unload = PymodCommand('unload')
    mp = mock_modulepath(modules_path.path)
    load('a')
    load('a1')
    load('a2')
    assert pymod.environ.get('a') == 'a'
    assert pymod.environ.get('a1') == 'a1'
    assert pymod.environ.get('a2') == 'a2'

    # a was "loaded" 3  times, loading b causes the
    unload('a2')
    a = pymod.modulepath.get('a')
    assert a.is_loaded
    unload('a1')
    assert a.is_loaded
    unload('a')
    assert not a.is_loaded
