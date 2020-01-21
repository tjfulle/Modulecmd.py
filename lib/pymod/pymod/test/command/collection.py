import os
import pytest

import pymod.mc
import pymod.paths
import pymod.environ
import pymod.collection
from pymod.main import PymodCommand
from pymod.error import CollectionNotFoundError


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
    a = pymod.mc.load("a")
    b = pymod.mc.load("b")
    c = pymod.mc.load("c")
    d = pymod.mc.load("d")

    collection("save", "foo")

    pymod.mc.purge()
    assert not a.is_loaded
    assert not b.is_loaded
    assert not c.is_loaded
    assert not d.is_loaded

    collection("restore", "foo")
    for x in "abcd":
        m = pymod.modulepath.get(x)
        assert m.is_loaded

    pymod.mc.purge()

    collection("show", "foo")

    collection("remove", "foo")
    assert pymod.collection.get("foo") is None


def test_command_collection_restore_bad(modules_path, mock_modulepath):
    collection = PymodCommand("collection")
    with pytest.raises(CollectionNotFoundError):
        collection("restore", "fake")


def test_command_collection_basic2(modules_path, mock_modulepath):

    mock_modulepath(modules_path.path)
    collection = PymodCommand("collection")
    a = pymod.mc.load("a")
    b = pymod.mc.load("b")
    c = pymod.mc.load("c")
    d = pymod.mc.load("d")

    collection("save", "foo")

    pymod.mc.purge()
    assert not a.is_loaded
    assert not b.is_loaded
    assert not c.is_loaded
    assert not d.is_loaded

    collection("restore", "foo")
    for x in "abcd":
        m = pymod.modulepath.get(x)
        assert m.is_loaded

    collection("avail")
    collection("avail", "-t")
    collection("avail", "--terse")
    collection("avail", "foo")


def test_command_collection_add_pop(modules_path, mock_modulepath):

    mock_modulepath(modules_path.path)
    collection = PymodCommand("collection")
    a = pymod.mc.load("a")
    b = pymod.mc.load("b")
    c = pymod.mc.load("c")

    collection("save", "foo")
    collection("restore", "foo")
    collection("add", "d")
    collection("pop", "a")
