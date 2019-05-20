import pytest

import pymod.mc
import pymod.error
import pymod.environ


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds
    tmpdir.join('a.py').write(m.setenv('module_swap', 'a'))
    tmpdir.join('b.py').write(m.setenv('module_swap', 'b'))
    tmpdir.join('c.py').write(m.swap('a', 'b'))
    tmpdir.join('d.py').write(m.swap('a', 'spam'))
    tmpdir.join('e.py').write(m.swap('spam', 'a'))
    tmpdir.join('f.py').write(m.swap('a', 'b'))
    ns = namespace()
    ns.path = tmpdir.strpath
    return ns


@pytest.mark.unit
def test_mc_swap_1(modules_path, mock_modulepath):
    mp = mock_modulepath(modules_path.path)
    pymod.mc.load('a')
    assert pymod.environ.get('module_swap') == 'a'
    pymod.mc.swap('a', 'b')
    assert pymod.environ.get('module_swap') == 'b'


def test_mc_swap_2(modules_path, mock_modulepath):
    mp = mock_modulepath(modules_path.path)
    a = pymod.mc.load('a')
    assert a.is_loaded
    assert pymod.environ.get('module_swap') == 'a'
    c = pymod.mc.load('c')
    b = pymod.modulepath.get('b')
    assert pymod.environ.get('module_swap') == 'b'
    assert c.is_loaded
    assert b.is_loaded
    assert not a.is_loaded

    # Module b is loaded, nothing to do
    pymod.mc.load('f')
    assert pymod.environ.get('module_swap') == 'b'
    pymod.mc.unload('f')
    pymod.mc.unload('c')

    # Unload b and then load c.  a is not loaded, but b should still be
    pymod.mc.unload('b')
    assert pymod.environ.get('module_swap') is None
    pymod.mc.load('c')
    assert pymod.environ.get('module_swap') == 'b'


def test_mc_swap_3(modules_path, mock_modulepath):
    mp = mock_modulepath(modules_path.path)
    pymod.mc.load('a')
    with pytest.raises(pymod.error.ModuleNotFoundError):
        pymod.mc.load('d')
    with pytest.raises(pymod.error.ModuleNotFoundError):
        pymod.mc.load('e')
    pymod.mc.load('c')
    assert pymod.environ.get('module_swap') == 'b'


def test_mc_swap_use(tmpdir, mock_modulepath):
    two = tmpdir.mkdir('2')
    two.join('b.py').write('')
    two.join('c.py').write('')

    one = tmpdir.mkdir('1')
    one.join('a.py').write('use({0!r})'.format(two.strpath))
    one.join('c.py').write('')
    one.join('d.py').write('')

    mp = mock_modulepath(one.strpath)
    with pytest.raises(pymod.error.ModuleNotFoundError):
        pymod.mc.load('b')

    a = pymod.mc.load('a')
    b = pymod.mc.load('b')
    c = pymod.mc.load('c')
    assert c.is_loaded
    assert c.modulepath == two.strpath

    # Now, swap a and d, b will be left unavailable, c will swap with the
    # version in `one`
    pymod.mc.swap('a', 'd')
    assert pymod.mc._mc._unloaded_on_mp_change[0] == b
    c = pymod.modulepath.get('c')
    assert c.is_loaded
    assert c.modulepath == one.strpath


def test_mc_swap_use_opts(tmpdir, mock_modulepath):
    content = """\
add_option('+x')
opts = parse_opts()
assert opts.x == 'foo'"""

    foo = tmpdir.mkdir('foo')
    a = foo.mkdir('a')
    a.join('1.0.py').write(content)

    baz = tmpdir.mkdir('baz')
    a = baz.mkdir('a')
    a.join('1.0.py').write(content)

    core = tmpdir.mkdir('core')
    core.join('foo.py').write('family("spam")\nuse({0!r})'.format(foo.strpath))
    core.join('baz.py').write('family("spam")\nuse({0!r})'.format(baz.strpath))

    mp = mock_modulepath(core.strpath)

    pymod.mc.load('foo')
    pymod.mc.load('a', opts=['+x=foo'])

    # swapping will load baz/a/1.0.py and the opts should also be preserved
    pymod.mc.swap('foo', 'baz')


def test_mc_swap_use_2(tmpdir, mock_modulepath):
    foo = tmpdir.mkdir('foo')
    a = foo.mkdir('a')
    a.join('2.0.py').write('')

    baz = tmpdir.mkdir('baz')
    a = baz.mkdir('a')
    a.join('1.0.py').write('')

    core = tmpdir.mkdir('core')
    core.join('foo.py').write('use({0!r})'.format(foo.strpath))
    core.join('baz.py').write('use({0!r})'.format(baz.strpath))

    mp = mock_modulepath(core.strpath)

    foo_module = pymod.mc.load('foo')
    foo_a = pymod.mc.load('a')

    baz_module = pymod.modulepath.get('baz')
    pymod.mc.swap_impl(foo_module, baz_module, maintain_state=True)
    assert len(pymod.mc._mc._unloaded_on_mp_change) == 0
    baz_a = pymod.modulepath.get('a')
    assert baz_a.modulepath == baz.strpath
