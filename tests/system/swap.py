import pytest

import modulecmd.system
import modulecmd.error
import modulecmd.environ


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds
    tmpdir.join("a.py").write(m.setenv("module_swap", "a"))
    tmpdir.join("b.py").write(m.setenv("module_swap", "b"))
    tmpdir.join("c.py").write(m.swap("a", "b"))
    tmpdir.join("d.py").write(m.swap("a", "spam"))
    tmpdir.join("e.py").write(m.swap("spam", "a"))
    tmpdir.join("f.py").write(m.swap("a", "b"))
    ns = namespace()
    ns.path = tmpdir.strpath
    return ns


def test_mc_swap_1(modules_path, mock_modulepath):
    mock_modulepath(modules_path.path)
    modulecmd.system.load("a")
    assert modulecmd.environ.get("module_swap") == "a"
    modulecmd.system.swap("a", "b")
    assert modulecmd.environ.get("module_swap") == "b"


def test_mc_swap_2(modules_path, mock_modulepath):
    mock_modulepath(modules_path.path)
    a = modulecmd.system.load("a")
    assert a.is_loaded
    assert modulecmd.environ.get("module_swap") == "a"
    c = modulecmd.system.load("c")
    b = modulecmd.modulepath.get("b")
    assert modulecmd.environ.get("module_swap") == "b"
    assert c.is_loaded
    assert b.is_loaded
    assert not a.is_loaded

    # Module b is loaded, nothing to do
    modulecmd.system.load("f")
    assert modulecmd.environ.get("module_swap") == "b"
    modulecmd.system.unload("f")
    modulecmd.system.unload("c")

    # Unload b and then load c.  a is not loaded, but b should still be
    modulecmd.system.unload("b")
    assert modulecmd.environ.get("module_swap") is None
    modulecmd.system.load("c")
    assert modulecmd.environ.get("module_swap") == "b"


def test_mc_swap_3(modules_path, mock_modulepath):
    mock_modulepath(modules_path.path)
    modulecmd.system.load("a")
    with pytest.raises(modulecmd.error.ModuleNotFoundError):
        modulecmd.system.load("d")
    with pytest.raises(modulecmd.error.ModuleNotFoundError):
        modulecmd.system.load("e")
    modulecmd.system.load("c")
    assert modulecmd.environ.get("module_swap") == "b"


def test_mc_swap_use(tmpdir, mock_modulepath):
    two = tmpdir.mkdir("2")
    two.join("b.py").write("")
    two.join("c.py").write("")

    one = tmpdir.mkdir("1")
    one.join("a.py").write("use({0!r})".format(two.strpath))
    one.join("c.py").write("")
    one.join("d.py").write("")

    mock_modulepath(one.strpath)
    with pytest.raises(modulecmd.error.ModuleNotFoundError):
        modulecmd.system.load("b")

    a = modulecmd.system.load("a")
    b = modulecmd.system.load("b")
    c = modulecmd.system.load("c")
    assert c.is_loaded
    assert c.modulepath == two.strpath

    # Now, swap a and d, b will be left unavailable, c will swap with the
    # version in `one`
    modulecmd.system.swap("a", "d")
    assert modulecmd.system.state._unloaded_on_mp_change[0] == b
    c = modulecmd.modulepath.get("c")
    assert c.is_loaded
    assert c.modulepath == one.strpath


def test_mc_swap_use_opts(tmpdir, mock_modulepath):
    content = """\
add_option('x')
assert opts.x == 'foo'"""

    foo = tmpdir.mkdir("foo")
    a = foo.mkdir("a")
    a.join("1.0.py").write(content)

    baz = tmpdir.mkdir("baz")
    a = baz.mkdir("a")
    a.join("1.0.py").write(content)

    core = tmpdir.mkdir("core")
    core.join("foo.py").write('family("spam")\nuse({0!r})'.format(foo.strpath))
    core.join("baz.py").write('family("spam")\nuse({0!r})'.format(baz.strpath))

    mock_modulepath(core.strpath)

    modulecmd.system.load("foo")
    modulecmd.system.load("a", opts={"x": "foo"})

    # swapping will load baz/a/1.0.py and the opts should also be preserved
    modulecmd.system.swap("foo", "baz")


def test_mc_swap_use_2(tmpdir, mock_modulepath):
    foo = tmpdir.mkdir("foo")
    a = foo.mkdir("a")
    a.join("2.0.py").write("")

    baz = tmpdir.mkdir("baz")
    a = baz.mkdir("a")
    a.join("1.0.py").write("")

    core = tmpdir.mkdir("core")
    core.join("foo.py").write("use({0!r})".format(foo.strpath))
    core.join("baz.py").write("use({0!r})".format(baz.strpath))

    mock_modulepath(core.strpath)

    foo_module = modulecmd.system.load("foo")
    foo_a = modulecmd.system.load("a")

    baz_module = modulecmd.modulepath.get("baz")
    # Since maintain_state is requested, the module `a` will not be reloaded
    modulecmd.system.swap_impl(foo_module, baz_module, maintain_state=True)
    assert len(modulecmd.system.state._unloaded_on_mp_change) == 1
    baz_a = modulecmd.modulepath.get("a")
    assert baz_a.modulepath == baz.strpath


def test_mc_swap_use_3(tmpdir, mock_modulepath):
    foo = tmpdir.mkdir("foo")
    a = foo.mkdir("a")
    a.join("2.0.py").write("")

    baz = tmpdir.mkdir("baz")
    a = baz.mkdir("a")
    a.join("1.0.py").write("")

    core = tmpdir.mkdir("core")
    core.join("foo.py").write("use({0!r})".format(foo.strpath))
    core.join("baz.py").write("use({0!r})".format(baz.strpath))

    mock_modulepath(core.strpath)

    foo_module = modulecmd.system.load("foo")
    foo_a = modulecmd.system.load("a")

    baz_module = modulecmd.modulepath.get("baz")
    # Since maintain_state is not requested, the module a will be reloaded, but from baz
    modulecmd.system.swap_impl(foo_module, baz_module)
    assert len(modulecmd.system.state._unloaded_on_mp_change) == 0
    baz_a = modulecmd.modulepath.get("a")
    assert baz_a.modulepath == baz.strpath


def test_mc_swap_use_4(tmpdir, mock_modulepath):
    foo = tmpdir.mkdir("foo")
    a = foo.mkdir("a")
    a.join("2.0.py").write("")

    baz = tmpdir.mkdir("baz")
    a = baz.mkdir("a")
    a.join("1.0.py").write("")

    core = tmpdir.mkdir("core")
    core.join("foo.py").write("use({0!r})".format(foo.strpath))
    core.join("baz.py").write("use({0!r})".format(baz.strpath))

    mock_modulepath(core.strpath)

    foo_module = modulecmd.system.load("foo")
    foo_a = modulecmd.system.load("a/2.0")

    baz_module = modulecmd.modulepath.get("baz")
    # Since a's name+version was used to load it, the module a will not be
    # reloaded since the a/2.0 does not exist in baz
    modulecmd.system.swap_impl(foo_module, baz_module)
    assert len(modulecmd.system.state._unloaded_on_mp_change) == 1
    baz_a = modulecmd.modulepath.get("a")
    assert baz_a.modulepath == baz.strpath


def test_mc_swap_use_5(tmpdir, mock_modulepath):
    foo = tmpdir.mkdir("foo")
    a = foo.mkdir("a")
    a.join("1.0.py").write("")

    baz = tmpdir.mkdir("baz")
    a = baz.mkdir("a")
    a.join("1.0.py").write("")
    a.join("2.0.py").write("")

    core = tmpdir.mkdir("core")
    core.join("foo.py").write("use({0!r})".format(foo.strpath))
    core.join("baz.py").write("use({0!r})".format(baz.strpath))

    mock_modulepath(core.strpath)

    foo_module = modulecmd.system.load("foo")
    foo_a = modulecmd.system.load("a/1.0")
    assert foo_a.acquired_as == foo_a.fullname

    baz_module = modulecmd.modulepath.get("baz")
    # Since a's name+version was used to load it, the module a will be
    # reloaded since the a/1.0 does not exist in baz
    modulecmd.system.swap_impl(foo_module, baz_module)
    assert len(modulecmd.system.state._unloaded_on_mp_change) == 0
    baz_a = modulecmd.modulepath.get("a/1.0")
    assert baz_a.modulepath == baz.strpath
    assert baz_a.is_loaded
