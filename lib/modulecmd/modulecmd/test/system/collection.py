import os
import pytest

import modulecmd.system
import modulecmd.paths
import modulecmd.environ
import modulecmd.collection
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
    two = tmpdir.mkdir("2")
    two.join("c.py").write(m.setenv("c"))
    two.join("d.py").write(m.setenv("d"))

    ns = namespace()
    ns.path = [one.strpath, two.strpath]
    return ns


@pytest.mark.unit
def test_mc_restore_good(modules_path, mock_modulepath):

    mock_modulepath(modules_path.path)
    a = modulecmd.system.load("a")
    b = modulecmd.system.load("b")
    c = modulecmd.system.load("c")
    d = modulecmd.system.load("d")

    modulecmd.system.save_collection("foo")
    assert modulecmd.collection.contains("foo")
    x = modulecmd.collection.get("foo")
    assert len(x) == 2

    modulecmd.system.purge()
    assert not a.is_loaded
    assert not b.is_loaded
    assert not c.is_loaded
    assert not d.is_loaded

    modulecmd.system.restore_collection("foo")
    assert a.is_loaded
    assert b.is_loaded
    assert c.is_loaded
    assert d.is_loaded

    modulecmd.system.show_collection("foo")


@pytest.mark.unit
def test_mc_restore_bad(modules_path, mock_modulepath):
    with pytest.raises(CollectionNotFoundError):
        modulecmd.system.restore_collection("fake")
