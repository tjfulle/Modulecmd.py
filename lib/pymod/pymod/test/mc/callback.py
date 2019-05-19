import os
import pytest

import pymod.mc
import pymod.error
import pymod.modes
import pymod.environ

"""Test of the callback functions sent to modules"""


def test_mc_callback_path_ops():
    append_path = pymod.mc.callback.append_path
    prepend_path = pymod.mc.callback.prepend_path
    remove_path = pymod.mc.callback.remove_path

    append_path(pymod.modes.load, None, 'foo', 'bar', sep=';')
    prepend_path(pymod.modes.load, None, 'foo', 'baz', sep=';')
    assert pymod.environ.get('foo') == 'baz;bar'
    remove_path(pymod.modes.load, None, 'foo', 'bar', sep=';')
    remove_path(pymod.modes.load, None, 'foo', 'baz', sep=';')
    assert pymod.environ.get('foo') is None

    append_path(pymod.modes.load, None, 'foo', 'bar', sep=';')
    prepend_path(pymod.modes.load, None, 'foo', 'baz', sep=';')
    assert pymod.environ.get('foo') == 'baz;bar'
    append_path(pymod.modes.unload, None, 'foo', 'bar', sep=';')
    prepend_path(pymod.modes.unload, None, 'foo', 'baz', sep=';')
    assert pymod.environ.get('foo') is None


def test_mc_callback_conflict(tmpdir, mock_modulepath):
    conflict = pymod.mc.callback.conflict
    tmpdir.join('a.py').write('')
    tmpdir.join('b.py').write('')
    mp = mock_modulepath(tmpdir.strpath)
    a = pymod.modulepath.get('a')

    b = pymod.mc.load('b')
    x = pymod.config.get('resolve_conflicts')
    pymod.config.set('resolve_conflicts', False)
    with pytest.raises(pymod.error.ModuleConflictError):
        conflict(pymod.modes.load, a, 'b')

    pymod.config.set('resolve_conflicts', True)
    conflict(pymod.modes.load, a, 'b')

    pymod.config.set('resolve_conflicts', x)

    b = pymod.mc.unload('b')
    conflict(pymod.modes.load, a, 'b')


def test_mc_callback_prereq(tmpdir, mock_modulepath):
    prereq = pymod.mc.callback.prereq
    prereq_any = pymod.mc.callback.prereq_any
    tmpdir.join('a.py').write('')
    tmpdir.join('b.py').write('')
    mp = mock_modulepath(tmpdir.strpath)

    with pytest.raises(pymod.error.PrereqMissingError):
        prereq(pymod.modes.load, None, 'b')

    pymod.mc.load('b')
    prereq(pymod.modes.load, None, 'b')
    prereq_any(pymod.modes.load, None, 'x', 'y', 'b')
    with pytest.raises(pymod.error.PrereqMissingError):
        prereq_any(pymod.modes.load, None, 'x', 'y', 'z')


def test_mc_callback_set_alias():
    set_alias = pymod.mc.callback.set_alias
    unset_alias = pymod.mc.callback.unset_alias

    set_alias(pymod.modes.load, None, 'foo', 'bar')
    assert pymod.environ.environ.aliases['foo'] == 'bar'
    set_alias(pymod.modes.unload, None, 'foo', 'bar')
    assert pymod.environ.environ.aliases['foo'] is None

    set_alias(pymod.modes.load, None, 'foo', 'bar')
    assert pymod.environ.environ.aliases['foo'] == 'bar'
    unset_alias(pymod.modes.load, None, 'foo')
    assert pymod.environ.environ.aliases['foo'] is None

    set_alias(pymod.modes.load, None, 'foo', 'bar')
    assert pymod.environ.environ.aliases['foo'] == 'bar'
    unset_alias(pymod.modes.unload, None, 'foo')
    assert pymod.environ.environ.aliases['foo'] == 'bar'


def test_mc_callback_set_shell_function():
    set_shell_function = pymod.mc.callback.set_shell_function
    unset_shell_function = pymod.mc.callback.unset_shell_function

    set_shell_function(pymod.modes.load, None, 'foo', 'bar')
    assert pymod.environ.environ.shell_functions['foo'] == 'bar'
    set_shell_function(pymod.modes.unload, None, 'foo', 'bar')
    assert pymod.environ.environ.shell_functions['foo'] is None

    set_shell_function(pymod.modes.load, None, 'foo', 'bar')
    assert pymod.environ.environ.shell_functions['foo'] == 'bar'
    unset_shell_function(pymod.modes.load, None, 'foo')
    assert pymod.environ.environ.shell_functions['foo'] is None

    set_shell_function(pymod.modes.load, None, 'foo', 'bar')
    assert pymod.environ.environ.shell_functions['foo'] == 'bar'
    unset_shell_function(pymod.modes.unload, None, 'foo')
    assert pymod.environ.environ.shell_functions['foo'] == 'bar'


def test_mc_callback_source(tmpdir, capsys):
    baz = tmpdir.join('baz')
    baz.write('echo BAZ')
    pymod.mc.callback.source(pymod.modes.load, None, baz.strpath)
    captured = capsys.readouterr()
    command = r'source {0};'.format(baz.strpath)
    assert captured[0].strip() == command.strip()

    with pytest.raises(ValueError):
        pymod.mc.callback.source(pymod.modes.load, None, 'fake.txt')


def test_mc_callback_load(tmpdir, mock_modulepath):
    load = pymod.mc.callback.load
    swap = pymod.mc.callback.swap
    unload = pymod.mc.callback.unload
    load_first = pymod.mc.callback.load_first

    tmpdir.join('a.py').write('')
    mp = mock_modulepath(tmpdir.strpath)

    with pytest.raises(pymod.error.ModuleNotFoundError):
        load(pymod.modes.load, None, 'x')

    with pytest.raises(pymod.error.ModuleNotFoundError):
        load(pymod.modes.load, None, 'x')

    # Even though `x` is not a module, unloading does not throw
    unload(pymod.modes.load, None, 'x')

    load(pymod.modes.load, None, 'a')
    a = pymod.modulepath.get('a')
    assert a.is_loaded

    unload(pymod.modes.load, None, 'a')
    assert not a.is_loaded

    load(pymod.modes.unload, None, 'a')
    assert not a.is_loaded

    load(pymod.modes.load, None, 'a')
    assert a.is_loaded

    unload(pymod.modes.unload, None, 'a')
    assert a.is_loaded

    with pytest.raises(pymod.error.ModuleNotFoundError):
        load_first(pymod.modes.load, None, 'x', 'y', 'z')
    load_first(pymod.modes.load, None, 'x', 'y', 'z', None)
    load_first(pymod.modes.load, None, 'x', 'y', 'a')
    a = pymod.modulepath.get('a')
    assert a.is_loaded


def test_mc_callback_swap(tmpdir, mock_modulepath):
    swap = pymod.mc.callback.swap
    tmpdir.join('a.py').write('')
    tmpdir.join('b.py').write('')
    mp = mock_modulepath(tmpdir.strpath)

    a = pymod.mc.load('a')
    assert a.is_loaded

    b = pymod.modulepath.get('b')
    assert not b.is_loaded

    swap(pymod.modes.unload, None, 'a', 'b')
    assert a.is_loaded
    assert not b.is_loaded

    swap(pymod.modes.load, None, 'a', 'b')
    assert not a.is_loaded
    assert b.is_loaded


def test_mc_callback_is_loaded(tmpdir, mock_modulepath):
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


def test_mc_callback_modulepath_ops(tmpdir, mock_modulepath):
    one = tmpdir.mkdir('1')
    one.join('a.py').write('')
    one.join('x.py').write('')
    two = tmpdir.mkdir('2')
    two.join('a.py').write('')

    mp = mock_modulepath(one.strpath)
    x = pymod.modulepath.get('x')  # just to set `unlocks`
    a = pymod.modulepath.get('a')
    assert a.filename == os.path.join(one.strpath, 'a.py')

    pymod.mc.callback.append_path(
        pymod.modes.load, x,
        pymod.names.modulepath,
        two.strpath)
    a = pymod.modulepath.get('a')
    assert a.filename == os.path.join(one.strpath, 'a.py')
    assert x.unlocks(two.strpath)

    pymod.mc.callback.remove_path(
        pymod.modes.load, x,
        pymod.names.modulepath,
        two.strpath)
    a = pymod.modulepath.get('a')
    assert a.filename == os.path.join(one.strpath, 'a.py')

    pymod.mc.callback.prepend_path(
        pymod.modes.load, x,
        pymod.names.modulepath,
        two.strpath)
    a = pymod.modulepath.get('a')
    assert a.filename == os.path.join(two.strpath, 'a.py')
    assert x.unlocks(two.strpath)


def test_mc_callback_stop(tmpdir, mock_modulepath):
    tmpdir.join('a.py').write(
        'setenv("a", "baz")\n'
        'stop()\n'
        'setenv("b", "foo")\n')
    mp = mock_modulepath(tmpdir.strpath)
    pymod.mc.load('a')
    assert pymod.environ.get('a') == 'baz'
    assert pymod.environ.get('b') is None


def test_mc_callback_setenv():
    setenv = pymod.mc.callback.setenv
    unsetenv = pymod.mc.callback.unsetenv

    setenv(pymod.modes.load, None, 'foo', 'bar')
    assert pymod.environ.environ['foo'] == 'bar'
    setenv(pymod.modes.unload, None, 'foo', 'bar')
    assert pymod.environ.environ['foo'] is None

    setenv(pymod.modes.load, None, 'foo', 'bar')
    assert pymod.environ.environ['foo'] == 'bar'
    unsetenv(pymod.modes.load, None, 'foo')
    assert pymod.environ.environ['foo'] is None

    setenv(pymod.modes.load, None, 'foo', 'bar')
    assert pymod.environ.environ['foo'] == 'bar'
    unsetenv(pymod.modes.unload, None, 'foo')
    assert pymod.environ.environ['foo'] == 'bar'


def test_mc_callback_family(tmpdir, mock_modulepath):
    family = pymod.mc.callback.family
    tmpdir.mkdir('ucc').join('1.2.py').write('')
    mp = mock_modulepath(tmpdir.strpath)
    module = pymod.modulepath.get('ucc')
    family_name = 'compiler'
    family(pymod.modes.load, module, family_name)
    assert pymod.environ.environ['MODULE_FAMILY_COMPILER'] == 'ucc'
    assert pymod.environ.environ['MODULE_FAMILY_COMPILER_VERSION'] == '1.2'

    family(pymod.modes.unload, module, family_name)
    assert pymod.environ.environ['MODULE_FAMILY_COMPILER'] is None
    assert pymod.environ.environ['MODULE_FAMILY_COMPILER_VERSION'] is None

    pymod.environ.environ['MODULE_FAMILY_COMPILER'] = 'ucc'
    pymod.environ.environ['MODULE_FAMILY_COMPILER_VERSION'] = '2.0'
    with pytest.raises(pymod.error.FamilyLoadedError):
        family(pymod.modes.load, module, family_name)


def test_mc_callback_help(tmpdir, mock_modulepath):
    help = pymod.mc.callback.help
    tmpdir.join('a.py').write('')
    mp = mock_modulepath(tmpdir.strpath)
    a = pymod.modulepath.get('a')
    helpstr = 'a help string'
    help(pymod.modes.load, a, helpstr)
    assert a._helpstr == helpstr


def test_mc_callback_whatis(tmpdir, mock_modulepath):
    whatis = pymod.mc.callback.whatis
    tmpdir.join('a.py').write('')
    tmpdir.join('b').write('#%Module1.0')
    mp = mock_modulepath(tmpdir.strpath)
    a = pymod.modulepath.get('a')
    whatis_str = 'a whatis string'
    whatis(pymod.modes.load, a, whatis_str)
    assert a._whatis['explicit'][0] == whatis_str
    whatis(pymod.modes.load, a, name='foo', version='x',
           short_description='a short description',
           foo='baz')
    assert a.name == 'foo'
    assert a.version.string == 'x'
    assert a._whatis['Foo'] == 'baz'
    assert a.short_description == 'a short description'

    b = pymod.modulepath.get('b')
    whatis(pymod.modes.load, b, whatis_str)
    assert b.short_description == whatis_str
    with pytest.raises(ValueError):
        whatis(pymod.modes.load, b, whatis_str, whatis_str, whatis_str)


def test_mc_callback_use(tmpdir, mock_modulepath):
    use = pymod.mc.callback.use
    unuse = pymod.mc.callback.unuse
    one = tmpdir.mkdir('1')
    one.join('x.py').write('')
    one.join('a.py').write('')
    one.join('b.py').write('')
    two = tmpdir.mkdir('2')
    two.join('a.py').write('')
    two.join('b.py').write('')
    mp = mock_modulepath(one.strpath)

    x = pymod.modulepath.get('x')
    a = pymod.modulepath.get('a')
    assert a.modulepath == one.strpath
    b = pymod.modulepath.get('b')
    assert b.modulepath == one.strpath

    use(pymod.modes.load, x, two.strpath, append=True)
    assert x.unlocks(two.strpath)
    assert pymod.modulepath.contains(two.strpath)
    a = pymod.modulepath.get('a')
    assert a.modulepath == one.strpath
    b = pymod.modulepath.get('b')
    assert b.modulepath == one.strpath

    use(pymod.modes.unload, x, two.strpath, append=True)
    assert x.unlocks(two.strpath)
    assert not pymod.modulepath.contains(two.strpath)
    a = pymod.modulepath.get('a')
    assert a.modulepath == one.strpath
    b = pymod.modulepath.get('b')
    assert b.modulepath == one.strpath

    use(pymod.modes.load, x, two.strpath)
    assert x.unlocks(two.strpath)
    assert pymod.modulepath.contains(two.strpath)
    a = pymod.modulepath.get('a')
    assert a.modulepath == two.strpath
    b = pymod.modulepath.get('b')
    assert b.modulepath == two.strpath

    unuse(pymod.modes.load, x, two.strpath)
    assert not pymod.modulepath.contains(two.strpath)
    a = pymod.modulepath.get('a')
    assert a.modulepath == one.strpath
    b = pymod.modulepath.get('b')
    assert b.modulepath == one.strpath
