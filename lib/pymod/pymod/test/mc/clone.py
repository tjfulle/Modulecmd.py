import os
import pytest

import pymod.mc
import pymod.paths
import pymod.environ
import pymod.collection


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds
    one = tmpdir.mkdir('1')
    one.join('a.py').write(m.setenv('a'))
    one.join('b.py').write(m.setenv('b'))
    one.join('c.py').write(m.setenv('c'))
    ns = namespace()
    ns.path = one.strpath
    return ns


@pytest.mark.unit
def test_clone(modules_path, mock_modulepath):
    """Just load and then unload a"""
    mp = mock_modulepath(modules_path.path)
    a = pymod.mc.load('a')
    b = pymod.mc.load('b')
    c = pymod.mc.load('c')
    assert a.is_loaded
    assert b.is_loaded
    assert c.is_loaded
    pymod.environ.set('foo', 'baz')
    pymod.environ.append_path('spam', 'bar')
    pymod.environ.prepend_path('spam', 'ham')
    assert pymod.environ.environ['foo'] == 'baz'
    assert pymod.environ.environ['spam'] == 'ham:bar'
    pymod.mc.clone('the-clone')
    pymod.mc.purge()
    assert not a.is_loaded
    assert not b.is_loaded
    assert not c.is_loaded
    pymod.environ.environ['foo'] = None
    pymod.environ.environ['spam'] = None
    pymod.mc.restore_clone('the-clone')
    modules = ''.join(sorted(pymod.mc._mc.loaded_module_names()))
    assert modules == 'abc'
    assert pymod.environ.environ['foo'] == 'baz'
    assert pymod.environ.environ['spam'] == 'ham:bar'
