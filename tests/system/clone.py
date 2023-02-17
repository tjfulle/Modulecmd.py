import os
import pytest

import modulecmd.system
import modulecmd.paths
import modulecmd.environ
import modulecmd.collection


def test_mc_clone(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write('setenv("a", "a")\n')
    tmpdir.join("b.py").write('setenv("b", "b")\n')
    tmpdir.join("c.py").write('setenv("c", "c")\n')
    mock_modulepath(tmpdir.strpath)
    a = modulecmd.system.load("a")
    b = modulecmd.system.load("b")
    c = modulecmd.system.load("c")
    assert a.is_loaded
    assert b.is_loaded
    assert c.is_loaded
    modulecmd.environ.set("foo", "baz")
    modulecmd.environ.append_path("spam", "bar")
    modulecmd.environ.prepend_path("spam", "ham")
    assert modulecmd.environ.environ["foo"] == "baz"
    assert modulecmd.environ.environ["spam"] == "ham:bar"
    modulecmd.system.save_clone("the-clone")
    modulecmd.system.purge()
    assert not a.is_loaded
    assert not b.is_loaded
    assert not c.is_loaded
    modulecmd.environ.environ["foo"] = None
    modulecmd.environ.environ["spam"] = None
    modulecmd.system.restore_clone("the-clone")
    modules = "".join(sorted([_.fullname for _ in modulecmd.system.loaded_modules()]))
    assert modules == "abc"
    assert modulecmd.environ.environ["foo"] == "baz"
    assert modulecmd.environ.environ["spam"] == "ham:bar"
    modulecmd.system.remove_clone("the-clone")


def test_mc_clone_bad(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write('setenv("a", "a")\n')
    tmpdir.join("b.py").write('setenv("b", "b")\n')
    tmpdir.join("c.py").write('setenv("c", "c")\n')
    mock_modulepath(tmpdir.strpath)
    a = modulecmd.system.load("a")
    b = modulecmd.system.load("b")
    c = modulecmd.system.load("c")
    assert a.is_loaded
    assert b.is_loaded
    assert c.is_loaded
    modulecmd.environ.set("foo", "baz")
    modulecmd.environ.append_path("spam", "bar")
    modulecmd.environ.prepend_path("spam", "ham")
    assert modulecmd.environ.environ["foo"] == "baz"
    assert modulecmd.environ.environ["spam"] == "ham:bar"
    modulecmd.system.save_clone("the-clone")
    modulecmd.system.purge()
    assert not a.is_loaded
    assert not b.is_loaded
    assert not c.is_loaded
    modulecmd.environ.environ["foo"] = None
    modulecmd.environ.environ["spam"] = None
    os.remove(tmpdir.join("a.py").strpath)
    with pytest.raises(modulecmd.error.CloneModuleNotFoundError):
        modulecmd.system.restore_clone("the-clone")
