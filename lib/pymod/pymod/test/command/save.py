import os
import pytest

import pymod.mc
import pymod.paths
import pymod.environ
import pymod.collection
from pymod.main import PymodCommand
from pymod.error import CollectionNotFoundError


@pytest.fixture(scope="function", autouse=True)
def collection(tmpdir):
    real_collection = pymod.collection.collections
    filename = os.path.join(tmpdir.strpath, "collections.json")
    pymod.collection.collections = pymod.collection.Collections(filename)
    yield tmpdir.strpath
    pymod.collection.collections = real_collection


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds
    one = tmpdir.mkdir("1")
    one.join("a.py").write(m.setenv("a"))
    one.join("b.py").write(m.setenv("b"))
    one.join("b2.py").write(m.setenv("b2"))
    two = tmpdir.mkdir("2")
    two.join("c.py").write(m.setenv("c"))
    two.join("d.py").write(m.setenv("d"))

    ns = namespace()
    ns.path = [one.strpath, two.strpath]
    return ns


def test_command_save(modules_path, mock_modulepath):

    mock_modulepath(modules_path.path)
    save = PymodCommand("save")
    restore = PymodCommand("restore")
    a = pymod.mc.load("a")
    b = pymod.mc.load("b")
    c = pymod.mc.load("c")
    d = pymod.mc.load("d")

    save("foo")

    pymod.mc.purge()
    assert not a.is_loaded
    assert not b.is_loaded
    assert not c.is_loaded
    assert not d.is_loaded

    b2 = pymod.mc.load("b2")

    restore("foo")
    assert a.is_loaded
    assert b.is_loaded
    assert c.is_loaded
    assert d.is_loaded
    assert not b2.is_loaded

    cat = PymodCommand("cat")
    cat("foo")


def test_command_restore_bad(modules_path, mock_modulepath):
    with pytest.raises(CollectionNotFoundError):
        pymod.mc.collection.restore("fake")


def test_command_remove(modules_path, mock_modulepath):

    mock_modulepath(modules_path.path)
    save = PymodCommand("save")
    remove = PymodCommand("remove")
    a = pymod.mc.load("a")
    b = pymod.mc.load("b")
    c = pymod.mc.load("c")
    d = pymod.mc.load("d")

    save("foo")
    assert pymod.collection.contains("foo")

    remove("foo")
    assert not pymod.collection.contains("foo")
