import os
import pytest

import pymod.mc
import pymod.paths
import pymod.environ
import pymod.collection


def test_mc_clone(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write('setenv("a", "a")\n')
    tmpdir.join("b.py").write('setenv("b", "b")\n')
    tmpdir.join("c.py").write('setenv("c", "c")\n')
    mock_modulepath(tmpdir.strpath)
    a = pymod.mc.load("a")
    b = pymod.mc.load("b")
    c = pymod.mc.load("c")
    assert a.is_loaded
    assert b.is_loaded
    assert c.is_loaded
    pymod.environ.set("foo", "baz")
    pymod.environ.append_path("spam", "bar")
    pymod.environ.prepend_path("spam", "ham")
    assert pymod.environ.environ["foo"] == "baz"
    assert pymod.environ.environ["spam"] == "ham:bar"
    pymod.mc.clone.save("the-clone")
    pymod.mc.purge()
    assert not a.is_loaded
    assert not b.is_loaded
    assert not c.is_loaded
    pymod.environ.environ["foo"] = None
    pymod.environ.environ["spam"] = None
    pymod.mc.clone.restore("the-clone")
    modules = "".join(sorted([_.fullname for _ in pymod.mc.get_loaded_modules()]))
    assert modules == "abc"
    assert pymod.environ.environ["foo"] == "baz"
    assert pymod.environ.environ["spam"] == "ham:bar"
    pymod.mc.clone.remove("the-clone")


def test_mc_clone_bad(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write('setenv("a", "a")\n')
    tmpdir.join("b.py").write('setenv("b", "b")\n')
    tmpdir.join("c.py").write('setenv("c", "c")\n')
    mock_modulepath(tmpdir.strpath)
    a = pymod.mc.load("a")
    b = pymod.mc.load("b")
    c = pymod.mc.load("c")
    assert a.is_loaded
    assert b.is_loaded
    assert c.is_loaded
    pymod.environ.set("foo", "baz")
    pymod.environ.append_path("spam", "bar")
    pymod.environ.prepend_path("spam", "ham")
    assert pymod.environ.environ["foo"] == "baz"
    assert pymod.environ.environ["spam"] == "ham:bar"
    pymod.mc.clone.save("the-clone")
    pymod.mc.purge()
    assert not a.is_loaded
    assert not b.is_loaded
    assert not c.is_loaded
    pymod.environ.environ["foo"] = None
    pymod.environ.environ["spam"] = None
    os.remove(tmpdir.join("a.py").strpath)
    with pytest.raises(pymod.error.CloneModuleNotFoundError):
        pymod.mc.clone.restore("the-clone")
