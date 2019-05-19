import os
import pytest

import pymod.mc
import pymod.error
import pymod.modes
import pymod.environ

"""Test module callback functions by actually executing the module"""


def test_mc_execmodule_path_ops(tmpdir, modulecmds, mock_modulepath):
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
    mp = mock_modulepath(tmpdir.strpath)

    c = pymod.mc.load('c')
    assert pymod.environ.get('spam') == 'eggs;ham'
    d = pymod.mc.load('d')
    assert pymod.environ.get('spam') is None

    pymod.mc.load('a')
    assert pymod.environ.get('foo') == 'baz:bar'
    pymod.mc.load('b')
    assert pymod.environ.get('foo') is None

    c = pymod.mc.unload('b')
    c = pymod.mc.unload('a')
    c = pymod.mc.unload('d')
    c = pymod.mc.unload('c')


def test_mc_execmodule_conflict(tmpdir, modulecmds, mock_modulepath):
    m = modulecmds
    tmpdir.join('a.py').write(m.setenv('a')+m.setenv('__x__')+m.unsetenv('__x__'))
    tmpdir.join('b.py').write(m.conflict('a'))
    mp = mock_modulepath(tmpdir.strpath)
    a = pymod.mc.load('a')
    with pytest.raises(pymod.error.ModuleConflictError):
        b = pymod.mc.load('b')


def test_mc_execmodule_prereq(tmpdir, modulecmds, mock_modulepath):
    m = modulecmds
    tmpdir.join('a.py').write(m.setenv('a'))
    tmpdir.join('b.py').write(m.prereq('a'))
    tmpdir.join('c.py').write(m.prereq_any('x', 'y', 'b'))
    mp = mock_modulepath(tmpdir.strpath)
    a = pymod.mc.load('a')
    # no problem, prereq a is loaded
    b = pymod.mc.load('b')

    pymod.mc.unload('b')
    pymod.mc.unload('a')

    # If we unload a, b will error out
    with pytest.raises(pymod.error.PrereqMissingError):
        pymod.mc.load('b')

    pymod.mc.unload('b')
    pymod.mc.unload('a')

    with pytest.raises(pymod.error.PrereqMissingError):
        pymod.mc.load('c')

    pymod.mc.load('a')
    pymod.mc.load('b')
    pymod.mc.load('c')


def test_mc_execmodule_set_alias(tmpdir, modulecmds, mock_modulepath):
    m = modulecmds
    tmpdir.join('a.py').write(m.set_alias('foo', 'bar'))
    tmpdir.join('b.py').write(m.unset_alias('foo'))
    mp = mock_modulepath(tmpdir.strpath)
    a = pymod.mc.load('a')
    assert pymod.environ.environ.aliases['foo'] == 'bar'
    b = pymod.mc.load('b')
    assert pymod.environ.environ.aliases['foo'] is None
    pymod.mc.unload('a')
    a = pymod.mc.load('a')
    assert pymod.environ.environ.aliases['foo'] == 'bar'
    pymod.mc.unload('a')
    assert pymod.environ.environ.aliases['foo'] is None


def test_mc_execmodule_set_shell_function(tmpdir, modulecmds, mock_modulepath):
    m = modulecmds
    tmpdir.join('a.py').write(m.set_shell_function('baz', 'bar $@'))
    tmpdir.join('b.py').write(m.unset_shell_function('baz'))
    mp = mock_modulepath(tmpdir.strpath)
    a = pymod.mc.load('a')
    assert pymod.environ.environ.shell_functions['baz'] == 'bar $@'
    b = pymod.mc.load('b')
    assert pymod.environ.environ.shell_functions['baz'] is None
    pymod.mc.unload('a')
    a = pymod.mc.load('a')
    assert pymod.environ.environ.shell_functions['baz'] == 'bar $@'
    pymod.mc.unload('a')
    assert pymod.environ.environ.shell_functions['baz'] is None


def test_mc_execmodule_source(tmpdir, modulecmds, mock_modulepath, capsys):
    m = modulecmds
    baz = tmpdir.join('baz')
    baz.write('echo BAZ')
    tmpdir.join('a.py').write(m.source(baz.strpath))
    mp = mock_modulepath(tmpdir.strpath)
    a = pymod.mc.load('a')
    captured = capsys.readouterr()
    command = 'source {0};'.format(baz.strpath)
    assert captured[0].strip() == command.strip()


def test_mc_execmodule_load_first(tmpdir, mock_modulepath):
    mp = mock_modulepath(tmpdir.strpath)
    with pytest.raises(pymod.error.ModuleNotFoundError):
        pymod.mc.callback.load_first(pymod.modes.load, 'x', 'y', 'z')
    pymod.mc.callback.load_first(pymod.modes.load, 'x', 'y', 'z', None)


def test_mc_execmodule_is_loaded(tmpdir, mock_modulepath):
    tmpdir.join('a.py').write('')
    tmpdir.join('b.py').write(
        'if is_loaded("fake"):\n'
        '    stop()\n'
        'if is_loaded("a"):\n'
        '    raise ValueError("a loaded!")\n')
    mp = mock_modulepath(tmpdir.strpath)
    pymod.mc.load('a')
    with pytest.raises(ValueError):
        pymod.mc.load('b')


def test_mc_execmodule_modulepath_ops(tmpdir, mock_modulepath):
    one = tmpdir.mkdir('1')
    one.join('a.py').write('')
    two = tmpdir.mkdir('2')
    two.join('a.py').write('')
    core = tmpdir.mkdir('core')
    x = core.mkdir('x')
    f1 = x.join('1.py').write('append_path({0!r}, {1!r})'.format(
        pymod.names.modulepath, one.strpath))
    f2 = x.join('2.py').write('prepend_path({0!r}, {1!r})'.format(
        pymod.names.modulepath, two.strpath))
    mp = mock_modulepath(core.strpath)

    x = pymod.mc.load('x/1')
    a = pymod.modulepath.get('a')
    assert a.filename == os.path.join(one.strpath, 'a.py')
    assert x.unlocks(one.strpath)

    x = pymod.mc.load('x/2')
    a = pymod.modulepath.get('a')
    assert a.filename == os.path.join(two.strpath, 'a.py')
    assert x.unlocks(two.strpath)


def test_mc_execmodule_stop(tmpdir, mock_modulepath):
    tmpdir.join('a.py').write(
        'setenv("a", "baz")\n'
        'stop()\n'
        'setenv("b", "foo")\n')
    mp = mock_modulepath(tmpdir.strpath)
    pymod.mc.load('a')
    assert pymod.environ.get('a') == 'baz'
    assert pymod.environ.get('b') is None
