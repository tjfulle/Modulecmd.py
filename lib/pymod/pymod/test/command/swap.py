import os
import pytest

import pymod.mc
import pymod.environ
from pymod.main import PymodCommand


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds
    one = tmpdir.mkdir('1')
    one.join('a.py').write(m.setenv('a'))
    one.join('b.py').write(m.setenv('b'))
    ns = namespace()
    ns.one = one.strpath
    return ns


def test_command_swap(modules_path, mock_modulepath):
    load = PymodCommand('load')
    swap = PymodCommand('swap')
    mp = mock_modulepath(modules_path.one)
    load('a')
    loaded = ''.join(pymod.mc._mc.loaded_module_names())
    assert loaded == 'a'
    swap('a', 'b')
    loaded = ''.join(pymod.mc._mc.loaded_module_names())
    assert loaded == 'b'
