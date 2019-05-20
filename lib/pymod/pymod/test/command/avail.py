import pytest

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


def test_command_avail(modules_path, mock_modulepath):
    load = PymodCommand('load')
    avail = PymodCommand('avail')
    save = PymodCommand('save')
    mock_modulepath([modules_path.one, modules_path.two])
    load('a')
    load('b')
    load('c')
    load('d', '+x=foo')
    save('foo')
    avail()
    avail('-t')
    avail('--terse')
    avail('a') # regular expression
    avail('--terse', 'a') # regular expression
