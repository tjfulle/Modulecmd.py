import os
import pytest

import pymod.mc
import pymod.error
import pymod.environ


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds
    tmpdir.join('a.py').write(m.setenv('a'))
    tmpdir.join('b.py').write(m.setenv('b'))
    tmpdir.join('c.py').write(m.setenv('c'))
    tmpdir.join('d.py').write(m.setenv('d')+m.load('e'))
    tmpdir.join('e.py').write(m.setenv('d'))
    ns = namespace()
    ns.path = tmpdir.strpath
    return ns


@pytest.mark.unit
def test_purge(modules_path, mock_modulepath):
    mp = mock_modulepath(modules_path.path)
    a = pymod.mc.load('a')
    b = pymod.mc.load('a')
    c = pymod.mc.load('a')
    d = pymod.mc.load('a')
    assert a.is_loaded
    assert b.is_loaded
    assert c.is_loaded
    assert d.is_loaded
    pymod.mc.purge()
    assert not a.is_loaded
    assert not b.is_loaded
    assert not c.is_loaded
    assert not d.is_loaded
