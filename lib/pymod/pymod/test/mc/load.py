import pytest

import pymod.mc
import pymod.environ
from pymod.error import ModuleNotFoundError


def test_mc_load_1(tmpdir, mock_modulepath):
    """Just load and then unload a"""
    tmpdir.join("a.py").write('setenv("__AA__", "AA")')
    mock_modulepath(tmpdir.strpath)
    a = pymod.mc.load("a")
    assert a.refcount == 1
    assert pymod.environ.get("__AA__") == "AA"
    pymod.mc.unload("a")
    assert pymod.environ.get("__AA__") is None
    assert a.refcount == 0


def test_mc_load_2(tmpdir, mock_modulepath):
    """Load a and b, b loads c, d, e. Then, unload b (c, d, e should also
    unload)
    """
    tmpdir.join("a.py").write('setenv("a", "a")')
    tmpdir.join("b.py").write('setenv("b", "b")\nload("c")')
    tmpdir.join("c.py").write('setenv("c", "c")\nload("d")')
    tmpdir.join("d.py").write('setenv("d", "d")\nload("e")')
    tmpdir.join("e.py").write('setenv("e", "e")')
    mock_modulepath(tmpdir.strpath)

    pymod.mc.load("a")
    assert pymod.environ.get("a") == "a"

    pymod.mc.load("b")
    for x in "bcde":
        assert pymod.environ.get(x) == x
        assert pymod.mc.module_is_loaded(x)
        m = pymod.modulepath.get(x)
        assert pymod.mc.module_is_loaded(m)
        assert pymod.mc.module_is_loaded(m.filename)

    # just unload e
    pymod.mc.unload("d")
    assert pymod.environ.get("d") is None
    assert pymod.environ.get("e") is None

    # unload b, c and d also unload
    pymod.mc.unload("b")
    assert pymod.environ.get("b") is None
    assert pymod.environ.get("c") is None
    assert pymod.environ.get("d") is None
    assert pymod.environ.get("a") == "a"

    pymod.mc.unload("a")
    assert pymod.environ.get("a") is None


def test_mc_load_3(tmpdir, mock_modulepath):
    """Load a and b, b loads d. Then, unload b (d should also unload)"""
    tmpdir.join("a.py").write('setenv("a", "a")\n')
    tmpdir.join("b.py").write('setenv("b", "b")\nload_first("c","e","d")\n')
    tmpdir.join("d.py").write('setenv("d", "d")\n')
    mock_modulepath(tmpdir.strpath)
    pymod.mc.load("a")
    assert pymod.environ.get("a") == "a"

    pymod.mc.load("b")
    for x in "ced":
        if x in "ce":
            assert pymod.environ.get(x) is None
            assert not pymod.mc.module_is_loaded(x)
        else:
            assert pymod.environ.get(x) == x
            assert pymod.mc.module_is_loaded(x)

    # unload b, e will also unload
    pymod.mc.unload("b")
    assert pymod.environ.get("b") is None
    assert pymod.environ.get("c") is None
    assert pymod.environ.get("d") is None
    assert pymod.environ.get("e") is None
    assert pymod.environ.get("a") == "a"

    pymod.mc.unload("a")
    assert pymod.environ.get("a") is None


def test_mc_load_inserted(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write('setenv("a", "a")')
    tmpdir.join("b.py").write('setenv("b", "b")\nload("c")')
    tmpdir.join("c.py").write('setenv("c", "c")\nload("d")')
    tmpdir.join("d.py").write('setenv("d", "d")\nload("e")')
    tmpdir.join("e.py").write('setenv("e", "e")')
    mock_modulepath(tmpdir.strpath)

    pymod.mc.load("e")
    pymod.mc.load("a", insert_at=1)
    assert "".join(_.fullname for _ in pymod.mc.get_loaded_modules()) == "ae"


def test_mc_load_first(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write('load_first("x","y","z")\n')
    tmpdir.join("b.py").write('load_first("x","y","z",None)\n')
    mock_modulepath(tmpdir.strpath)
    with pytest.raises(ModuleNotFoundError):
        # None of the modules in the load_first command in module 'g' can be
        # found
        pymod.mc.load("a")
    # None of the modules in the load_first command in module 'g' can be found,
    # but the last is `None` so no error is issued
    b = pymod.mc.load("b")
    assert b.is_loaded


def test_mc_load_nvv(tmpdir, mock_modulepath):
    a = tmpdir.mkdir("a")
    a1 = a.mkdir("1.0")
    a1.join("base").write("#%Module1.0")
    a1.join("parallel").write("#%Module1.0")
    mock_modulepath(tmpdir.strpath)
    m = pymod.mc.load("a/1.0/base")
    assert m is not None
    assert m.name == "a"
    assert m.version.string == "1.0"
    assert m.variant == "base"


def test_mc_load_inserted_2(tmpdir, mock_modulepath):

    two = tmpdir.mkdir("2")
    two.join("b.py").write("")

    one = tmpdir.mkdir("1")
    one.join("a.py").write("")
    one.join("c.py").write("unuse({0!r})".format(two.strpath))

    mock_modulepath([one.strpath, two.strpath])

    a = pymod.mc.load("a")
    b = pymod.mc.load("b")
    c = pymod.mc.load("c", insert_at=1)
    assert not b.is_loaded

    assert len(pymod.mc._mc._unloaded_on_mp_change) == 1
    assert pymod.mc._mc._unloaded_on_mp_change[0] == b


def test_mc_load_inserted_3(tmpdir, mock_modulepath):

    foo = tmpdir.mkdir("foo")
    foo.join("a.py").write("")

    core = tmpdir.mkdir("core")
    core.join("a.py").write("")
    core.join("foo.py").write("use({0!r})".format(foo.strpath))

    mock_modulepath(core.strpath)

    a = pymod.mc.load("a")
    c = pymod.mc.load("foo", insert_at=1)
    xx = pymod.modulepath.get("a")
    assert not a.is_loaded
    assert xx.is_loaded
    assert xx.fullname == a.fullname


def test_mc_load_inserted_4(tmpdir, mock_modulepath):

    foo = tmpdir.mkdir("foo")
    a = foo.mkdir("a")
    a.join("2.0.py").write("")

    core = tmpdir.mkdir("core")
    a = core.mkdir("a")
    a.join("1.0.py").write("")
    core.join("foo.py").write("use({0!r})".format(foo.strpath))

    mock_modulepath(core.strpath)

    a = pymod.mc.load("a")
    assert a.modulepath == core.strpath
    assert a.version == "1.0"

    m = pymod.mc.load("foo", insert_at=1)
    a2 = pymod.modulepath.get("a")
    assert a2.modulepath == foo.strpath

    assert not a.is_loaded
    assert a2.is_loaded
    assert a2.name == a.name


def test_mc_load_inserted_with_opts(tmpdir, mock_modulepath):

    one = tmpdir.mkdir("1")
    a = one.mkdir("a")
    a.join("2.0.py").write('add_option("x")\n')
    one.join("b.py").write("")

    mock_modulepath(one.strpath)

    a = pymod.mc.load("a", opts={"x": "baz"})
    assert a.parse_opts().as_dict() == {"x": "baz"}

    b = pymod.mc.load("b", insert_at=1)
    assert a.is_loaded
    assert a.parse_opts().as_dict() == {"x": "baz"}


def test_mc_load_inserted_acqby(tmpdir, mock_modulepath):
    core = tmpdir.mkdir("core")
    a = core.mkdir("a")
    a.join("1.0.py").write("")
    a.join("2.0.py").write("")
    core.join("b.py").write("")

    mock_modulepath(core.strpath)

    a = pymod.mc.load("a")
    assert a.version == "2.0"

    b = pymod.mc.load("b", insert_at=1)

    ma = pymod.modulepath.get(core.join("a/2.0.py").strpath)
    assert ma.is_loaded

    pymod.mc.purge()

    a = pymod.mc.load("a/1.0")
    assert a.version == "1.0"

    b = pymod.mc.load("b", insert_at=1)

    ma = pymod.modulepath.get(core.join("a/1.0.py").strpath)
    assert ma.is_loaded

    pymod.mc._mc._loaded_modules = None
    modules = pymod.mc._mc.get_loaded_modules()
    assert ma in modules


def test_mc_load_bad_callback(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write('load("FAKE")')
    mock_modulepath(tmpdir.strpath)

    with pytest.raises(pymod.error.ModuleNotFoundError):
        pymod.mc.load("a")

    # Now hack the thing
    a = pymod.modulepath.get("a")
    a.acquired_as = a.name
    lm_cellar = [
        dict(
            fullname=a.fullname,
            filename=a.filename,
            family=a.family,
            opts=a.parse_opts().as_dict(),
            acquired_as=a.acquired_as,
        )
    ]
    pymod.environ.set(pymod.names.loaded_module_cellar, lm_cellar, serialize=True)
    pymod.mc._mc._loaded_modules = [a]

    # This should not error out, even though 'FAKE' does not exist.  This is by
    # design when unloading from a module
    pymod.mc.unload("a")
