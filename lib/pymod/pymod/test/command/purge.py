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
    one.join('d.py').write(m.setenv('d')+m.load('e'))
    one.join('e.py').write(m.setenv('e'))
    two = tmpdir.mkdir('2')
    two.join('a.py').write(m.setenv('a'))
    two.join('b.py').write(m.setenv('b')+m.load_first('c','e','d'))
    two.join('d.py').write(m.setenv('d'))
    two.join('g.py').write(m.setenv('b')+m.load_first('x','y','z',None))
    ns = namespace()
    ns.one = one.strpath
    ns.two = two.strpath
    return ns


def test_command_purge(modules_path, mock_modulepath):
    """Load a and b, b loads c, d, e. Then, unload b (c, d, e should also
    unload)
    """
    load = PymodCommand('load')
    purge = PymodCommand('purge')
    mock_modulepath(modules_path.one)
    load('a')
    assert pymod.environ.get('a') == 'a'

    load('b')
    for x in 'bcde':
        assert pymod.environ.get(x) == x
        assert pymod.mc.module_is_loaded(x)
    purge()

    loaded = pymod.mc.get_loaded_modules()
    assert len(loaded) == 0
