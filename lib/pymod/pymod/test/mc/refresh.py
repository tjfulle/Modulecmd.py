import pytest

import pymod.mc
import pymod.environ


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


def test_mc_refresh(modules_path, mock_modulepath):
    mp = mock_modulepath(modules_path.path)
    a = pymod.mc.load('a')
    b = pymod.mc.load('b')
    assert pymod.environ.get('a') == 'a'
    assert pymod.environ.get('b') == 'b'
    assert pymod.environ.get('c') == 'c'
    assert pymod.environ.get('d') == 'd'
    pymod.mc.refresh()
    assert pymod.environ.get('a') == 'a'
    assert pymod.environ.get('b') == 'b'
    assert pymod.environ.get('c') == 'c'
    assert pymod.environ.get('d') == 'd'
    # Reference count should not change
    assert pymod.mc.get_refcount(a) == 1
    assert pymod.mc.get_refcount(b) == 1
