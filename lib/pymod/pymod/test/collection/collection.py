import os
import pytest

import pymod.mc
import pymod.paths
import pymod.environ
import pymod.collection


@pytest.fixture(scope='function', autouse=True)
def collection(tmpdir):
    real_collection = pymod.collection.collections
    filename = os.path.join(tmpdir.strpath, 'collections.json')
    pymod.collection.collections = pymod.collection.Collections(filename)
    yield tmpdir.strpath
    pymod.collection.collections = real_collection


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds
    one = tmpdir.mkdir('1')
    one.join('a.py').write(m.setenv('a'))
    one.join('b.py').write(m.setenv('b'))
    two = tmpdir.mkdir('2')
    two.join('c.py').write(m.setenv('c'))
    two.join('d.py').write(m.setenv('d'))

    ns = namespace()
    ns.path = [one.strpath, two.strpath]
    return ns


@pytest.mark.unit
def test_collection_default(modules_path, mock_modulepath):

    mp = mock_modulepath(modules_path.path)
    a = pymod.mc.load('a')
    b = pymod.mc.load('b')
    pymod.mc.save(pymod.names.default_user_collection)
    assert pymod.collection.contains(pymod.names.default_user_collection)
    x = pymod.collection.get(pymod.names.default_user_collection)
    assert len(x) == 1
    assert len(x[0]) == 2
    assert len(x[0][1]) == 2
    assert x[0][0] == pymod.modulepath._path.path[0].path
    assert x[0][1][0][0] == 'a'
    assert x[0][1][1][0] == 'b'
    s = pymod.collection.format_available().split('\n')[1].strip()
    assert s == '(None)'


@pytest.mark.unit
def test_collection_named(modules_path, mock_modulepath):

    mp = mock_modulepath(modules_path.path)
    a = pymod.mc.load('a')
    b = pymod.mc.load('b')
    c = pymod.mc.load('c')
    d = pymod.mc.load('d', opts=['+x'])

    pymod.mc.save('foo')
    assert pymod.collection.contains('foo')
    x = pymod.collection.get('foo')
    assert len(x) == 2

    assert len(x[0]) == 2
    assert len(x[0][1]) == 2
    assert x[0][0] == pymod.modulepath._path.path[0].path
    assert x[0][1][0][0] == 'a'
    assert x[0][1][1][0] == 'b'

    assert len(x[1]) == 2
    assert len(x[1][1]) == 2
    assert x[1][0] == pymod.modulepath._path.path[1].path
    assert x[1][1][0][0] == 'c'
    assert x[1][1][1][0] == 'd'

    s = pymod.collection.format_available().split('\n')[1].strip()
    assert s == 'foo'

    s = pymod.collection.format_show('foo')

    pymod.mc.purge()
    pymod.mc.restore('foo')
    for x in 'abcd':
        assert pymod.modulepath.get(x) is not None

    pymod.mc.purge()

    # remove a module
    f = os.path.join(pymod.modulepath._path.path[0].path, 'a.py')
    os.remove(f)
    with pytest.raises(pymod.error.CollectionModuleNotFoundError):
        pymod.mc.restore('foo')

    pymod.collection.remove('foo')
    assert not pymod.collection.contains('foo')

    with pytest.raises(pymod.error.CollectionNotFoundError):
        pymod.mc.restore('foo')
