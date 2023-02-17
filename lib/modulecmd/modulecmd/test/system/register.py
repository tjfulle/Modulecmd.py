import pytest
import modulecmd.system
import modulecmd.error
import modulecmd.modulepath
from modulecmd.module import factory


def test_mc_register_1(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write("")
    mock_modulepath(tmpdir.strpath)
    a = modulecmd.modulepath.get("a")
    modulecmd.system.register_module(a)
    assert a.filename in [_.filename for _ in modulecmd.system.loaded_modules()]


def test_mc_register_2(tmpdir, mock_modulepath):
    value = modulecmd.config.get("skip_add_devpack")
    modulecmd.config.set("skip_add_devpack", True)
    tmpdir.join("devpack.py").write("")
    mock_modulepath(tmpdir.strpath)
    m = factory(tmpdir.strpath, "devpack.py")
    modulecmd.system.register_module(m)
    assert m.filename not in [_.filename for _ in modulecmd.system.loaded_modules()]
    modulecmd.config.set("skip_add_devpack", value)


def test_mc_register_3(tmpdir):
    tmpdir.join("a.py").write("")
    a = factory(tmpdir.strpath, "a.py")
    with pytest.raises(modulecmd.error.InconsistentModuleStateError):
        modulecmd.system.register_module(a)


def test_mc_refcount_decrement(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write("")
    mock_modulepath(tmpdir.strpath)
    a = modulecmd.modulepath.get("a")
    assert a.refcount == 0

    modulecmd.system.load("a")
    assert a.refcount == 1

    a.refcount += 1
    assert a.refcount == 2

    a.refcount -= 1
    modulecmd.system.unload("a")
    assert a.refcount == 0


def test_mc_refcount(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write("")
    a = factory(tmpdir.strpath, "a.py")
    a.refcount += 1
    assert a.refcount == 1

    a.refcount += 1
    assert a.refcount == 2

    a.refcount -= 1
    assert a.refcount == 1

    a.refcount -= 1
    assert a.refcount == 0

    with pytest.raises(ValueError):
        # This will put the reference count < 0
        a.refcount -= 1
