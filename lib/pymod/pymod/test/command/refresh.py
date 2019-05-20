import pytest

import pymod.mc
from pymod.main import PymodCommand


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds
    one = tmpdir.mkdir('1')
    one.join('a.py').write(m.setenv('a'))
    one.join('b.py').write(m.setenv('b'))
    one.join('c.py').write(m.setenv('c'))
    one.join('d.py').write(m.setenv('d'))
    ns = namespace()
    ns.one = one.strpath
    return ns


@pytest.mark.unit
def test_command_refresh(modules_path, mock_modulepath):
    load = PymodCommand('load')
    refresh = PymodCommand('refresh')
    mock_modulepath(modules_path.one)
    load('a', 'b', 'c', 'd')
    refresh()
    loaded = ''.join(pymod.mc._mc.loaded_module_names())
    assert loaded == 'abcd'
