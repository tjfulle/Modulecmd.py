import os
import pytest

from contrib.util import str2dict
import pymod.mc
import pymod.error
import pymod.environ

"""Test the different module callback functions that are not tested
elsewhere"""


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds
    tmpdir.join('a.py').write(
        m.append_path('foo', 'bar', sep=':') +
        m.prepend_path('foo', 'baz', sep=':'))
    tmpdir.join('b.py').write(
        m.remove_path('foo', 'baz') +
        m.remove_path('foo', 'bar'))

    tmpdir.join('c.py').write(
        m.append_path('spam', 'ham', sep=';') +
        m.prepend_path('spam', 'eggs', sep=';'))
    tmpdir.join('d.py').write(
        m.remove_path('spam', 'ham', sep=';')+
        m.remove_path('spam', 'eggs', sep=';'))

    tmpdir.join('e.py').write(m.setenv('e'))
    tmpdir.join('f.py').write(m.conflict('e'))

    tmpdir.join('g.py').write(m.setenv('g'))
    tmpdir.join('h.py').write(m.prereq('g'))
    tmpdir.join('i.py').write(m.prereq_any('a', 'b', 'h'))

    tmpdir.join('j.py').write(m.set_alias('foo', 'bar'))
    tmpdir.join('k.py').write(m.unset_alias('foo'))
    tmpdir.join('l.py').write(m.set_shell_function('baz', 'bar $@'))
    tmpdir.join('m.py').write(m.unset_shell_function('baz'))

    n_script = tmpdir.join('baz').write('echo BAZ')
    tmpdir.join('n.py').write(m.source(tmpdir.join('baz').strpath))

    ns = namespace()
    ns.path = tmpdir.strpath
    ns.n_script = tmpdir.join('baz').strpath
    return ns


@pytest.mark.unit
def test_path_ops(modules_path, mock_modulepath):
    """Just load and then unload a"""
    mp = mock_modulepath(modules_path.path)

    c = pymod.mc.load('c')
    assert pymod.environ.get('spam') == 'eggs;ham'
    d = pymod.mc.load('d')
    assert pymod.environ.get('spam') is None

    pymod.mc.load('a')
    assert pymod.environ.get('foo') == 'baz:bar'
    pymod.mc.load('b')
    assert pymod.environ.get('foo') is None


@pytest.mark.unit
def test_conflict(modules_path, mock_modulepath):
    """Just load and then unload a"""
    mp = mock_modulepath(modules_path.path)
    e = pymod.mc.load('e')
    with pytest.raises(pymod.error.ModuleConflictError):
        f = pymod.mc.load('f')


@pytest.mark.unit
def test_prereq(modules_path, mock_modulepath):
    mp = mock_modulepath(modules_path.path)
    g = pymod.mc.load('g')
    # no problem, prereq g is loaded
    h = pymod.mc.load('h')

    pymod.mc.unload('h')
    pymod.mc.unload('g')

    # If we unload g, h will error out
    with pytest.raises(pymod.error.PrereqMissingError):
        pymod.mc.load('h')

    pymod.mc.unload('h')
    pymod.mc.unload('g')

    with pytest.raises(pymod.error.PrereqMissingError):
        pymod.mc.load('i')

    pymod.mc.load('g')
    pymod.mc.load('h')
    pymod.mc.load('i')


@pytest.mark.unit
def test_set_alias(modules_path, mock_modulepath):
    mp = mock_modulepath(modules_path.path)
    j = pymod.mc.load('j')
    assert pymod.environ.environ.aliases['foo'] == 'bar'
    k = pymod.mc.load('k')
    assert pymod.environ.environ.aliases['foo'] is None
    pymod.mc.unload('j')
    j = pymod.mc.load('j')
    assert pymod.environ.environ.aliases['foo'] == 'bar'
    pymod.mc.unload('j')
    assert pymod.environ.environ.aliases['foo'] is None


@pytest.mark.unit
def test_set_shell_function(modules_path, mock_modulepath):
    mp = mock_modulepath(modules_path.path)
    l = pymod.mc.load('l')
    assert pymod.environ.environ.shell_functions['baz'] == 'bar $@'
    m = pymod.mc.load('m')
    assert pymod.environ.environ.shell_functions['baz'] is None
    pymod.mc.unload('l')
    l = pymod.mc.load('l')
    assert pymod.environ.environ.shell_functions['baz'] == 'bar $@'
    pymod.mc.unload('l')
    assert pymod.environ.environ.shell_functions['baz'] is None

@pytest.mark.unit
def test_source(modules_path, mock_modulepath, capsys):
    mp = mock_modulepath(modules_path.path)
    n = pymod.mc.load('n')
    captured = capsys.readouterr()
    command = r'source {};'.format(modules_path.n_script)
    assert captured[0].strip() == command.strip()
