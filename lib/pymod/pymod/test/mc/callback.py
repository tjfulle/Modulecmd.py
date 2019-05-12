import os
import pytest

import pymod.mc
import pymod.error
import pymod.modes
import pymod.environ
from contrib.util import str2dict

"""Test of the callback functions sent to modules"""


def test_mc_callback_path_ops():
    append_path = pymod.mc.callback.append_path
    prepend_path = pymod.mc.callback.prepend_path
    remove_path = pymod.mc.callback.remove_path

    append_path(pymod.modes.load, 'foo', 'bar', sep=';')
    prepend_path(pymod.modes.load, 'foo', 'baz', sep=';')
    assert pymod.environ.get('foo') == 'baz;bar'
    remove_path(pymod.modes.load, 'foo', 'bar', sep=';')
    remove_path(pymod.modes.load, 'foo', 'baz', sep=';')
    assert pymod.environ.get('foo') is None

    append_path(pymod.modes.load, 'foo', 'bar', sep=';')
    prepend_path(pymod.modes.load, 'foo', 'baz', sep=';')
    assert pymod.environ.get('foo') == 'baz;bar'
    append_path(pymod.modes.unload, 'foo', 'bar', sep=';')
    prepend_path(pymod.modes.unload, 'foo', 'baz', sep=';')
    assert pymod.environ.get('foo') is None


def test_mc_callback_conflict(tmpdir, mock_modulepath):
    conflict = pymod.mc.callback.conflict
    tmpdir.join('a.py').write('')
    tmpdir.join('b.py').write('')
    mp = mock_modulepath(tmpdir.strpath)
    a = pymod.modulepath.get('a')

    b = pymod.mc.load('b')
    with pytest.raises(pymod.error.ModuleConflictError):
        conflict(pymod.modes.load, 'b', module=a)

    b = pymod.mc.unload('b')
    conflict(pymod.modes.load, 'b', module=a)


def test_mc_callback_prereq(tmpdir, mock_modulepath):
    prereq = pymod.mc.callback.prereq
    prereq_any = pymod.mc.callback.prereq_any
    tmpdir.join('a.py').write('')
    tmpdir.join('b.py').write('')
    mp = mock_modulepath(tmpdir.strpath)

    with pytest.raises(pymod.error.PrereqMissingError):
        prereq(pymod.modes.load, 'b')

    pymod.mc.load('b')
    prereq(pymod.modes.load, 'b')
    prereq_any(pymod.modes.load, 'x', 'y', 'b')
    with pytest.raises(pymod.error.PrereqMissingError):
        prereq_any(pymod.modes.load, 'x', 'y', 'z')


def test_mc_callback_set_alias():
    set_alias = pymod.mc.callback.set_alias
    unset_alias = pymod.mc.callback.unset_alias

    set_alias(pymod.modes.load, 'foo', 'bar')
    assert pymod.environ.environ.aliases['foo'] == 'bar'
    set_alias(pymod.modes.unload, 'foo', 'bar')
    assert pymod.environ.environ.aliases['foo'] is None

    set_alias(pymod.modes.load, 'foo', 'bar')
    assert pymod.environ.environ.aliases['foo'] == 'bar'
    unset_alias(pymod.modes.load, 'foo')
    assert pymod.environ.environ.aliases['foo'] is None

    set_alias(pymod.modes.load, 'foo', 'bar')
    assert pymod.environ.environ.aliases['foo'] == 'bar'
    unset_alias(pymod.modes.unload, 'foo')
    assert pymod.environ.environ.aliases['foo'] == 'bar'


def test_mc_callback_set_shell_function():
    set_shell_function = pymod.mc.callback.set_shell_function
    unset_shell_function = pymod.mc.callback.unset_shell_function

    set_shell_function(pymod.modes.load, 'foo', 'bar')
    assert pymod.environ.environ.shell_functions['foo'] == 'bar'
    set_shell_function(pymod.modes.unload, 'foo', 'bar')
    assert pymod.environ.environ.shell_functions['foo'] is None

    set_shell_function(pymod.modes.load, 'foo', 'bar')
    assert pymod.environ.environ.shell_functions['foo'] == 'bar'
    unset_shell_function(pymod.modes.load, 'foo')
    assert pymod.environ.environ.shell_functions['foo'] is None

    set_shell_function(pymod.modes.load, 'foo', 'bar')
    assert pymod.environ.environ.shell_functions['foo'] == 'bar'
    unset_shell_function(pymod.modes.unload, 'foo')
    assert pymod.environ.environ.shell_functions['foo'] == 'bar'


def test_mc_callback_source(tmpdir, capsys):
    baz = tmpdir.join('baz')
    baz.write('echo BAZ')
    pymod.mc.callback.source(pymod.modes.load, baz.strpath)
    captured = capsys.readouterr()
    command = r'source {};'.format(baz.strpath)
    assert captured[0].strip() == command.strip()


def test_mc_callback_load(tmpdir, mock_modulepath):
    load = pymod.mc.callback.load
    swap = pymod.mc.callback.swap
    unload = pymod.mc.callback.unload
    load_first = pymod.mc.callback.load_first

    tmpdir.join('a.py').write('')
    mp = mock_modulepath(tmpdir.strpath)

    with pytest.raises(pymod.error.ModuleNotFoundError):
        load(pymod.modes.load, 'x')

    with pytest.raises(pymod.error.ModuleNotFoundError):
        load(pymod.modes.load, 'x')

    # Even though `x` is not a module, unloading does not throw
    unload(pymod.modes.load, 'x')

    load(pymod.modes.load, 'a')
    a = pymod.modulepath.get('a')
    assert a.is_loaded

    unload(pymod.modes.load, 'a')
    assert not a.is_loaded

    load(pymod.modes.unload, 'a')
    assert not a.is_loaded

    load(pymod.modes.load, 'a')
    assert a.is_loaded

    unload(pymod.modes.unload, 'a')
    assert a.is_loaded

    with pytest.raises(pymod.error.ModuleNotFoundError):
        load_first(pymod.modes.load, 'x', 'y', 'z')
    load_first(pymod.modes.load, 'x', 'y', 'z', None)
    load_first(pymod.modes.load, 'x', 'y', 'a')
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

    swap(pymod.modes.unload, 'a', 'b')
    assert a.is_loaded
    assert not b.is_loaded

    swap(pymod.modes.load, 'a', 'b')
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
    two = tmpdir.mkdir('2')
    two.join('a.py').write('')

    mp = mock_modulepath(one.strpath)
    a = pymod.modulepath.get('a')
    assert a.filename == os.path.join(one.strpath, 'a.py')

    pymod.mc.callback.append_path(
        pymod.modes.load,
        pymod.names.modulepath,
        two.strpath)
    a = pymod.modulepath.get('a')
    assert a.filename == os.path.join(one.strpath, 'a.py')

    pymod.mc.callback.remove_path(
        pymod.modes.load,
        pymod.names.modulepath,
        two.strpath)
    a = pymod.modulepath.get('a')
    assert a.filename == os.path.join(one.strpath, 'a.py')

    pymod.mc.callback.prepend_path(
        pymod.modes.load,
        pymod.names.modulepath,
        two.strpath)
    a = pymod.modulepath.get('a')
    assert a.filename == os.path.join(two.strpath, 'a.py')


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

    setenv(pymod.modes.load, 'foo', 'bar')
    assert pymod.environ.environ['foo'] == 'bar'
    setenv(pymod.modes.unload, 'foo', 'bar')
    assert pymod.environ.environ['foo'] is None

    setenv(pymod.modes.load, 'foo', 'bar')
    assert pymod.environ.environ['foo'] == 'bar'
    unsetenv(pymod.modes.load, 'foo')
    assert pymod.environ.environ['foo'] is None

    setenv(pymod.modes.load, 'foo', 'bar')
    assert pymod.environ.environ['foo'] == 'bar'
    unsetenv(pymod.modes.unload, 'foo')
    assert pymod.environ.environ['foo'] == 'bar'


def test_mc_callback_family(tmpdir, mock_modulepath):
    family = pymod.mc.callback.family
    tmpdir.mkdir('ucc').join('1.2.py').write('')
    mp = mock_modulepath(tmpdir.strpath)
    module = pymod.modulepath.get('ucc')
    family_name = 'compiler'
    family(pymod.modes.load, family_name, module=module)
    assert pymod.environ.environ['MODULE_FAMILY_COMPILER'] == 'ucc'
    assert pymod.environ.environ['MODULE_FAMILY_COMPILER_VERSION'] == '1.2'

    family(pymod.modes.unload, family_name, module=module)
    assert pymod.environ.environ['MODULE_FAMILY_COMPILER'] is None
    assert pymod.environ.environ['MODULE_FAMILY_COMPILER_VERSION'] is None

    pymod.environ.environ['MODULE_FAMILY_COMPILER'] = 'ucc'
    pymod.environ.environ['MODULE_FAMILY_COMPILER_VERSION'] = '2.0'
    with pytest.raises(pymod.error.FamilyLoadedError):
        family(pymod.modes.load, family_name, module=module)


def test_mc_callback_help(tmpdir, mock_modulepath):
    help = pymod.mc.callback.help
    tmpdir.join('a.py').write('')
    mp = mock_modulepath(tmpdir.strpath)
    a = pymod.modulepath.get('a')
    helpstr = 'a help string'
    help(pymod.modes.load, helpstr, module=a)
    assert a._helpstr == helpstr


def test_mc_callback_whatis(tmpdir, mock_modulepath):
    whatis = pymod.mc.callback.whatis
    tmpdir.join('a.py').write('')
    tmpdir.join('b').write('#%Module1.0')
    mp = mock_modulepath(tmpdir.strpath)
    a = pymod.modulepath.get('a')
    whatis_str = 'a whatis string'
    whatis(pymod.modes.load, whatis_str, module=a)
    assert a._whatis['explicit'][0] == whatis_str
    whatis(pymod.modes.load, name='foo', version='x',
           short_description='a short description',
           foo='baz', module=a)
    assert a.name == 'foo'
    assert a.version.string == 'x'
    assert a._whatis['Foo'] == 'baz'
    assert a.short_description == 'a short description'

    b = pymod.modulepath.get('b')
    whatis(pymod.modes.load, whatis_str, module=b)
    assert b.short_description == whatis_str
    with pytest.raises(ValueError):
        whatis(pymod.modes.load, whatis_str, whatis_str, whatis_str, module=b)


def test_mc_callback_use(tmpdir, mock_modulepath):
    use = pymod.mc.callback.use
    unuse = pymod.mc.callback.unuse
    one = tmpdir.mkdir('1')
    one.join('a.py').write('')
    one.join('b.py').write('')
    two = tmpdir.mkdir('2')
    two.join('a.py').write('')
    two.join('b.py').write('')
    mp = mock_modulepath(one.strpath)

    a = pymod.modulepath.get('a')
    assert a.modulepath == one.strpath
    b = pymod.modulepath.get('b')
    assert b.modulepath == one.strpath

    use(pymod.modes.load, two.strpath, append=True)
    assert pymod.modulepath.contains(two.strpath)
    a = pymod.modulepath.get('a')
    assert a.modulepath == one.strpath
    b = pymod.modulepath.get('b')
    assert b.modulepath == one.strpath

    use(pymod.modes.unload, two.strpath, append=True)
    assert not pymod.modulepath.contains(two.strpath)
    a = pymod.modulepath.get('a')
    assert a.modulepath == one.strpath
    b = pymod.modulepath.get('b')
    assert b.modulepath == one.strpath

    use(pymod.modes.load, two.strpath)
    assert pymod.modulepath.contains(two.strpath)
    a = pymod.modulepath.get('a')
    assert a.modulepath == two.strpath
    b = pymod.modulepath.get('b')
    assert b.modulepath == two.strpath

    unuse(pymod.modes.load, two.strpath)
    assert not pymod.modulepath.contains(two.strpath)
    a = pymod.modulepath.get('a')
    assert a.modulepath == one.strpath
    b = pymod.modulepath.get('b')
    assert b.modulepath == one.strpath
