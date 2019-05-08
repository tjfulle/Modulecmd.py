import os
import pytest

import pymod.mc
import pymod.error
import pymod.environ


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds
    one = tmpdir.mkdir('1')
    one.join('a.py').write(m.setenv('a'))
    one.join('b.py').write(m.setenv('b')+m.load('c'))
    one.join('c.py').write(m.setenv('c')+m.load('d'))
    one.join('d.py').write(m.setenv('d')+m.load('e'))
    two = tmpdir.mkdir('2')
    two.join('a.py').write(m.setenv('a'))
    two.join('b.py').write(m.setenv('b')+m.load_first('c','e','d'))
    two.join('d.py').write(m.setenv('d'))
    two.join('g.py').write(m.setenv('b')+m.load_first('x','y','z',None))
    ns = namespace()
    ns.one = one.strpath
    ns.two = two.strpath
    return ns


@pytest.mark.unit
def test_load_1(modules_path, mock_modulepath):
    """Just load and then unload a"""
    mp = mock_modulepath(modules_path.one)
    pymod.mc.load('a')
    assert pymod.environ.get('__a__') == '__a__'
    pymod.mc.unload('a')
    assert pymod.environ.get('__a__') is None


def test_load_2(modules_path, mock_modulepath):
    """Load a and b, b loads c, d, e. Then, unload b (c, d, e should also
    unload)
    """
    mp = mock_modulepath(modules_path.one)
    pymod.mc.load('a')
    assert pymod.environ.get('__a__') == '__a__'

    pymod.mc.load('b')
    for x in 'bcde':
        key = '__{}__'.format(x.upper())
        val = '__{}__'.format(x)
        assert pymod.environ.get(key) == val
        assert pymod.mc.module_is_loaded(x)

    # just unload e
    pymod.mc.unload('e')
    assert pymod.environ.get('__e__') is None

    # unload b, c and d also unload
    pymod.mc.unload('b')
    assert pymod.environ.get('__b__') is None
    assert pymod.environ.get('__c__') is None
    assert pymod.environ.get('__d__') is None
    assert pymod.environ.get('__a__') == '__a__'

    pymod.mc.unload('a')
    assert pymod.environ.get('__a__') is None


def test_load_3(modules_path, mock_modulepath):
    """Load a and b, b loads d. Then, unload b (d should also unload)"""
    mp = mock_modulepath(modules_path.two)
    pymod.mc.load('a')
    assert pymod.environ.get('__a__') == '__a__'

    pymod.mc.load('b')
    for x in 'ced':
        key = '__{}__'.format(x.upper())
        if x in 'ce':
            assert pymod.environ.get(key) is None
            assert not pymod.mc.module_is_loaded(x)
        else:
            val = '__{}__'.format(x)
            assert pymod.environ.get(key) == val
            assert pymod.mc.module_is_loaded(x)

    # unload b, e will also unload
    pymod.mc.unload('b')
    assert pymod.environ.get('__b__') is None
    assert pymod.environ.get('__c__') is None
    assert pymod.environ.get('__d__') is None
    assert pymod.environ.get('__e__') is None
    assert pymod.environ.get('__a__') == '__a__'

    pymod.mc.unload('a')
    assert pymod.environ.get('__a__') is None
