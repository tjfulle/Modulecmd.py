import os
import pytest

import modulecmd.system
import modulecmd.paths
import modulecmd.environ
import modulecmd.collection
from modulecmd.main import PymodCommand
from modulecmd.error import CollectionNotFoundError


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


def test_command_collection_basic(modules_path, mock_modulepath):

    mock_modulepath(modules_path.path)
    collection = PymodCommand("collection")
    a = modulecmd.system.load("a")
    b = modulecmd.system.load("b")
    c = modulecmd.system.load("c")
    d = modulecmd.system.load("d")

    collection("save", "foo")

    modulecmd.system.purge()
    assert not a.is_loaded
    assert not b.is_loaded
    assert not c.is_loaded
    assert not d.is_loaded

    collection("restore", "foo")
    for x in "abcd":
        m = modulecmd.modulepath.get(x)
        assert m.is_loaded

    modulecmd.system.purge()

    collection("show", "foo")

    collection("remove", "foo")
    assert modulecmd.collection.get("foo") is None


def test_command_collection_restore_bad(modules_path, mock_modulepath):
    collection = PymodCommand("collection")
    with pytest.raises(CollectionNotFoundError):
        collection("restore", "fake")


def test_command_collection_basic2(modules_path, mock_modulepath):

    mock_modulepath(modules_path.path)
    collection = PymodCommand("collection")
    a = modulecmd.system.load("a")
    b = modulecmd.system.load("b")
    c = modulecmd.system.load("c")
    d = modulecmd.system.load("d")

    collection("save", "foo")

    modulecmd.system.purge()
    assert not a.is_loaded
    assert not b.is_loaded
    assert not c.is_loaded
    assert not d.is_loaded

    collection("restore", "foo")
    for x in "abcd":
        m = modulecmd.modulepath.get(x)
        assert m.is_loaded

    collection("avail")
    collection("avail", "-t")
    collection("avail", "--terse")
    collection("avail", "foo")


def test_command_collection_add_pop(modules_path, mock_modulepath):

    mock_modulepath(modules_path.path)
    collection = PymodCommand("collection")
    a = modulecmd.system.load("a")
    b = modulecmd.system.load("b")
    c = modulecmd.system.load("c")

    collection("save", "foo")
    collection("restore", "foo")
    collection("add", "d")
    collection("pop", "a")
