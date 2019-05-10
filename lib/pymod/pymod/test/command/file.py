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
    ns = namespace()
    ns.one = one.strpath
    return ns


def test_file(modules_path, mock_modulepath):
    file = PymodCommand('file')
    mp = mock_modulepath(modules_path.one)
    file('a')