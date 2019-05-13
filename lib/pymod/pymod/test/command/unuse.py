import os
import pytest

import pymod.modulepath
from pymod.main import PymodCommand


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds
    one = tmpdir.mkdir('1')
    one.join('a.py').write(m.setenv('a'))
    one.join('b.py').write(m.setenv('b'))
    two = tmpdir.mkdir('2')
    two.join('a.py').write(m.setenv('a'))
    two.join('b.py').write(m.setenv('b'))
    three = tmpdir.mkdir('3')
    three.join('a.py').write(m.setenv('a'))
    three.join('b.py').write(m.setenv('b'))
    ns = namespace()
    ns.one = one.strpath
    ns.two = two.strpath
    ns.three = three.strpath
    return ns


@pytest.mark.unit
def test_command_unuse(modules_path, mock_modulepath):
    unuse = PymodCommand('unuse')
    mp = mock_modulepath([modules_path.one, modules_path.two])
    unuse(modules_path.two)
    unuse(modules_path.one)
    assert pymod.modulepath.size() == 0
