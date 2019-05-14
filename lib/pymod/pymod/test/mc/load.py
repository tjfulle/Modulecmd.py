import os
import pytest

import pymod.mc
import pymod.environ
from pymod.error import ModuleNotFoundError


@pytest.fixture()
def directory_tree(tmpdir, namespace, modulecmds):
    m = modulecmds
    one = tmpdir.mkdir('1')
    one.join('a.py').write(m.setenv('a'))
    one.join('b.py').write(m.setenv('b')+m.load('c'))
    one.join('c.py').write(m.setenv('c')+m.load('d'))
    one.join('d.py').write(m.setenv('d')+m.load('e'))
    one.join('e.py').write(m.setenv('e'))
    two = tmpdir.mkdir('2')
    two.join('a.py').write(m.setenv('a'))
    two.join('b.py').write(m.setenv('b')+m.load_first('c','e','d'))
    two.join('d.py').write(m.setenv('d'))
    three = tmpdir.mkdir('3')
    two.join('g.py').write(m.setenv('g')+m.load_first('x','y','z'))
    two.join('h.py').write(m.setenv('h')+m.load_first('x','y','z',None))
    ns = namespace()
    ns.one = one.strpath
    ns.two = two.strpath
    ns.three = two.strpath
    return ns


def test_mc_load_1(directory_tree, mock_modulepath):
    """Just load and then unload a"""
    mp = mock_modulepath(directory_tree.one)
    a = pymod.mc.load('a')
    assert pymod.mc.get_refcount(a) == 1
    assert pymod.mc.get_refcount().get(a.fullname) == 1
    assert pymod.environ.get('a') == 'a'
    pymod.mc.unload('a')
    assert pymod.environ.get('a') is None


def test_mc_load_2(directory_tree, mock_modulepath):
    """Load a and b, b loads c, d, e. Then, unload b (c, d, e should also
    unload)
    """
    mp = mock_modulepath(directory_tree.one)
    pymod.mc.load('a')
    assert pymod.environ.get('a') == 'a'

    pymod.mc.load('b')
    for x in 'bcde':
        assert pymod.environ.get(x) == x
        assert pymod.mc.module_is_loaded(x)
        m = pymod.modulepath.get(x)
        assert pymod.mc.module_is_loaded(m)
        assert pymod.mc.module_is_loaded(m.filename)

    # just unload e
    pymod.mc.unload('d')
    assert pymod.environ.get('d') is None
    assert pymod.environ.get('e') is None

    # unload b, c and d also unload
    pymod.mc.unload('b')
    assert pymod.environ.get('b') is None
    assert pymod.environ.get('c') is None
    assert pymod.environ.get('d') is None
    assert pymod.environ.get('a') == 'a'

    pymod.mc.unload('a')
    assert pymod.environ.get('a') is None


def test_mc_load_3(directory_tree, mock_modulepath):
    """Load a and b, b loads d. Then, unload b (d should also unload)"""
    mp = mock_modulepath(directory_tree.two)
    pymod.mc.load('a')
    assert pymod.environ.get('a') == 'a'

    pymod.mc.load('b')
    for x in 'ced':
        if x in 'ce':
            assert pymod.environ.get(x) is None
            assert not pymod.mc.module_is_loaded(x)
        else:
            assert pymod.environ.get(x) == x
            assert pymod.mc.module_is_loaded(x)

    # unload b, e will also unload
    pymod.mc.unload('b')
    assert pymod.environ.get('b') is None
    assert pymod.environ.get('c') is None
    assert pymod.environ.get('d') is None
    assert pymod.environ.get('e') is None
    assert pymod.environ.get('a') == 'a'

    pymod.mc.unload('a')
    assert pymod.environ.get('a') is None


def test_mc_load_inserted(directory_tree, mock_modulepath):
    mp = mock_modulepath(directory_tree.one)
    pymod.mc.load('e')
    pymod.mc.load('a', insert_at=1)
    assert ''.join(pymod.mc._mc.loaded_module_names()) == 'ae'


def test_mc_load_first(directory_tree, mock_modulepath):
    mp = mock_modulepath(directory_tree.three)
    with pytest.raises(ModuleNotFoundError):
        # None of the modules in the load_first command in module 'g' can be
        # found
        pymod.mc.load('g')
    # None of the modules in the load_first command in module 'g' can be found,
    # but the last is `None` so no error is issued
    h = pymod.mc.load('h')
    assert h.is_loaded


def test_mc_load_nvv(tmpdir, mock_modulepath):
    a = tmpdir.mkdir('a')
    a1 = a.mkdir('1.0')
    a1.join('base').write('#%Module1.0')
    a1.join('parallel').write('#%Module1.0')
    mock_modulepath(tmpdir.strpath)
    m = pymod.mc.load('a/1.0/base')
    assert m is not None
    assert m.name == 'a'
    assert m.version.string == '1.0'
    assert m.variant == 'base'
