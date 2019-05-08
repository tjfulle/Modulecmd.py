import os
import pytest

import pymod.mc
import pymod.error
import pymod.environ


@pytest.fixture()
def modules_path(tmpdir):
    one = tmpdir.mkdir('1')
    one.join('a.py').write("setenv('__A__', '__a__')")
    one.join('b.py').write("setenv('__B__', '__b__')\nload('c','d','e')")
    one.join('c.py').write("setenv('__C__', '__c__')")
    one.join('d.py').write("setenv('__D__', '__d__')")
    one.join('e.py').write("setenv('__E__', '__e__')")
    two = tmpdir.mkdir('2')
    two.join('a.py').write("setenv('__A__', '__a__')")
    two.join('b.py').write("setenv('__B__', '__b__')\nload_first('c','e','d')")
    two.join('d.py').write("setenv('__D__', '__d__')")
    return tmpdir


@pytest.mark.unit
def test_load_1(modules_path, mock_modulepath):
    """Just load and then unload a"""
    mp = mock_modulepath(modules_path.join('1').strpath)
    pymod.mc.load('a')
    assert pymod.environ.get('__A__') == '__a__'
    pymod.mc.unload('a')
    assert pymod.environ.get('__A__') is None


def test_load_2(modules_path, mock_modulepath):
    """Load a and b, b loads c, d, e. Then, unload b (c, d, e should also
    unload)
    """
    mp = mock_modulepath(modules_path.join('1').strpath)
    pymod.mc.load('a')
    assert pymod.environ.get('__A__') == '__a__'

    pymod.mc.load('b')
    for x in 'bcde':
        key = '__{}__'.format(x.upper())
        val = '__{}__'.format(x)
        assert pymod.environ.get(key) == val
        assert pymod.mc.module_is_loaded(x)

    # just unload e
    pymod.mc.unload('e')
    assert pymod.environ.get('__E__') is None

    # unload b, c and d also unload
    pymod.mc.unload('b')
    assert pymod.environ.get('__B__') is None
    assert pymod.environ.get('__C__') is None
    assert pymod.environ.get('__D__') is None
    assert pymod.environ.get('__A__') == '__a__'

    pymod.mc.unload('a')
    assert pymod.environ.get('__A__') is None


def test_load_3(modules_path, mock_modulepath):
    """Load a and b, b loads d. Then, unload b (d should also unload)"""
    mp = mock_modulepath(modules_path.join('2').strpath)
    pymod.mc.load('a')
    assert pymod.environ.get('__A__') == '__a__'

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
    assert pymod.environ.get('__B__') is None
    assert pymod.environ.get('__C__') is None
    assert pymod.environ.get('__D__') is None
    assert pymod.environ.get('__E__') is None
    assert pymod.environ.get('__A__') == '__a__'

    pymod.mc.unload('a')
    assert pymod.environ.get('__A__') is None
