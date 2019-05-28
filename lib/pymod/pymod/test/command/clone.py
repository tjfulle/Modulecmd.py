import os
import pytest

import pymod.mc
import pymod.paths
import pymod.environ
import pymod.collection
from pymod.main import PymodCommand
from pymod.error import CloneDoesNotExistError


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds
    one = tmpdir.mkdir('1')
    one.join('a.py').write(m.setenv('a'))
    one.join('b.py').write(m.setenv('b'))
    one.join('b2.py').write(m.setenv('b2'))
    two = tmpdir.mkdir('2')
    two.join('c.py').write(m.setenv('c'))
    two.join('d.py').write(m.setenv('d'))

    ns = namespace()
    ns.path = [one.strpath, two.strpath]
    return ns

def test_command_clone(modules_path, mock_modulepath):

    mock_modulepath(modules_path.path)
    clone = PymodCommand('clone')
    a = pymod.mc.load('a')
    b = pymod.mc.load('b')
    c = pymod.mc.load('c')
    d = pymod.mc.load('d')

    clone('save', 'foo')

    pymod.mc.purge()
    assert not a.is_loaded
    assert not b.is_loaded
    assert not c.is_loaded
    assert not d.is_loaded

    clone('restore', 'foo')
    for x in 'abcd':
        m = pymod.modulepath.get(x)
        assert m.is_loaded

    pymod.mc.purge()

    clone('remove', 'foo')
    assert pymod.clone.get('foo') is None


def test_command_restore_clone_bad(modules_path, mock_modulepath):
    clone = PymodCommand('clone')
    with pytest.raises(CloneDoesNotExistError):
        clone('restore', 'fake')


def test_command_clone2(modules_path, mock_modulepath):

    mock_modulepath(modules_path.path)
    clone = PymodCommand('clone')
    a = pymod.mc.load('a')
    b = pymod.mc.load('b')
    c = pymod.mc.load('c')
    d = pymod.mc.load('d')

    clone('save', 'foo')

    pymod.mc.purge()
    assert not a.is_loaded
    assert not b.is_loaded
    assert not c.is_loaded
    assert not d.is_loaded

    clone('restore', 'foo')
    for x in 'abcd':
        m = pymod.modulepath.get(x)
        assert m.is_loaded

    clone('avail')
    clone('avail', '-t')
    clone('avail', '--terse')
