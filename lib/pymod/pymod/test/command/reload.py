import pytest

import pymod.mc
import pymod.environ
from pymod.main import PymodCommand


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


@pytest.mark.unit
def test_command_reload_1(modules_path, mock_modulepath):
    load = PymodCommand('load')
    reload = PymodCommand('reload')
    mp = mock_modulepath(modules_path.path)
    load('a')
    assert pymod.environ.get('a') == 'a'
    reload('a')
    assert pymod.environ.get('a') == 'a'
    # Reference count should not change
    a = pymod.modulepath.get('a')
    assert pymod.mc.get_refcount(a) == 1


@pytest.mark.unit
def test_command_reload_2(modules_path, mock_modulepath):
    load = PymodCommand('load')
    reload = PymodCommand('reload')
    mp = mock_modulepath(modules_path.path)
    load('a')
    load('b')
    assert pymod.environ.get('a') == 'a'
    assert pymod.environ.get('b') == 'b'
    assert pymod.environ.get('c') == 'c'
    assert pymod.environ.get('d') == 'd'
    reload('a')
    assert pymod.environ.get('a') == 'a'
    # Reference count should not change
    a = pymod.modulepath.get('a')
    b = pymod.modulepath.get('b')
    assert pymod.mc.get_refcount(a) == 1
    assert pymod.mc.get_refcount(b) == 1
