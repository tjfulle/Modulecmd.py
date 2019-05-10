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
    one.join('b.py').write(m.setenv('b')+m.load('c'))
    one.join('c.py').write(m.setenv('c')+m.load('d'))
    one.join('d.py').write(m.setenv('d')+m.load('e'))
    one.join('e.py').write(m.setenv('e'))
    ns = namespace()
    ns.path = one.strpath
    return ns


def test_help(modules_path, mock_modulepath):
    help = PymodCommand('help')
    mp = mock_modulepath(modules_path.path)
    with pytest.raises(SystemExit):
        help('help', '-h')
