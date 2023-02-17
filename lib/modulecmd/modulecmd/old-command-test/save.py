import os
import pytest

import modulecmd.system
import modulecmd.paths
import modulecmd.environ
import modulecmd.collection
from modulecmd.main import PymodCommand
from modulecmd.error import CollectionNotFoundError


@pytest.fixture(scope="function", autouse=True)
def collection(tmpdir):
    real_collection = modulecmd.collection.collections
    filename = os.path.join(tmpdir.strpath, "collections.json")
    modulecmd.collection.collections = modulecmd.collection.Collections(filename)
    yield tmpdir.strpath
    modulecmd.collection.collections = real_collection


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
    a = modulecmd.system.load("a")
    b = modulecmd.system.load("b")
    c = modulecmd.system.load("c")
    d = modulecmd.system.load("d")

    save("foo")

    modulecmd.system.purge()
    assert not a.is_loaded
    assert not b.is_loaded
    assert not c.is_loaded
    assert not d.is_loaded

    b2 = modulecmd.system.load("b2")

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
        modulecmd.system.resore_collection("fake")


def test_command_remove(modules_path, mock_modulepath):

    mock_modulepath(modules_path.path)
    save = PymodCommand("save")
    remove = PymodCommand("remove")
    a = modulecmd.system.load("a")
    b = modulecmd.system.load("b")
    c = modulecmd.system.load("c")
    d = modulecmd.system.load("d")

    save("foo")
    assert modulecmd.collection.contains("foo")

    remove("foo")
    assert not modulecmd.collection.contains("foo")
