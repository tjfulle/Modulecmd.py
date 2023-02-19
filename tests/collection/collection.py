import os
import pytest

import modulecmd.system
import modulecmd.paths
import modulecmd.error
import modulecmd.environ
import modulecmd.collection


@pytest.fixture(scope="function", autouse=True)
def collection(tmpdir):
    assert modulecmd.collection.version() == (1, 0), "Wrong collection version!"
    real_collection = modulecmd.collection.collections
    filename = os.path.join(tmpdir.strpath, "collections.json")
    modulecmd.collection.collections = modulecmd.collection.Collections(filename)
    yield tmpdir.strpath
    modulecmd.collection.collections = real_collection


@pytest.fixture()
def modules(tmpdir, namespace, modulecmds):
    m = modulecmds
    one = tmpdir.mkdir("1")
    one.join("a.py").write(m.setenv("a"))
    one.join("b.py").write(m.setenv("b"))
    two = tmpdir.mkdir("2")
    two.join("c.py").write(m.setenv("c"))
    two.join("d.py").write(m.setenv("d") + '\nadd_option("x")')

    ns = namespace()
    ns.path = [one.strpath, two.strpath]
    return ns


def test_collection_default(modules, mock_modulepath):
    mock_modulepath(modules.path)
    a = modulecmd.system.load("a")
    b = modulecmd.system.load("b")
    modulecmd.system.save_collection(modulecmd.names.default_user_collection)
    assert modulecmd.collection.contains(modulecmd.names.default_user_collection)
    x = modulecmd.collection.get(modulecmd.names.default_user_collection)
    assert len(x) == 1
    assert len(x[0]) == 2
    assert len(x[0][1]) == 2
    assert x[0][0] == modulecmd.modulepath.path()[0]
    coll = x[0][1]
    assert coll[0]["fullname"] == "a"
    assert coll[1]["fullname"] == "b"


def test_collection_named(modules, mock_modulepath):

    mock_modulepath(modules.path)
    a = modulecmd.system.load("a")
    b = modulecmd.system.load("b")
    c = modulecmd.system.load("c")
    d = modulecmd.system.load("d", opts={"x": True})

    modulecmd.system.save_collection("foo")
    assert modulecmd.collection.contains("foo")
    x = modulecmd.collection.get("foo")
    assert len(x) == 2

    assert len(x[0]) == 2
    assert len(x[0][1]) == 2
    assert x[0][0] == modulecmd.modulepath.path()[0]

    coll = x[0][1]
    assert coll[0]["fullname"] == "a"
    assert coll[1]["fullname"] == "b"

    assert len(x[1]) == 2
    assert len(x[1][1]) == 2
    assert x[1][0] == modulecmd.modulepath.path()[1]

    coll = x[1][1]
    assert coll[0]["fullname"] == "c"
    assert coll[1]["fullname"] == "d"

    s = modulecmd.collection.show("foo")

    modulecmd.system.purge()
    modulecmd.system.restore_collection("foo")
    for x in "abcd":
        assert modulecmd.modulepath.get(x) is not None

    modulecmd.system.purge()

    # remove a module
    f = os.path.join(modulecmd.modulepath.path()[0], "a.py")
    os.remove(f)
    with pytest.raises(modulecmd.error.CollectionModuleNotFoundError):
        modulecmd.system.restore_collection("foo")

    modulecmd.collection.remove("foo")
    assert not modulecmd.collection.contains("foo")

    with pytest.raises(modulecmd.error.CollectionNotFoundError):
        modulecmd.system.restore_collection("foo")


def test_collection_add_pop(modules, mock_modulepath):
    mock_modulepath(modules.path)
    a = modulecmd.system.load("a")
    b = modulecmd.system.load("b")
    d = modulecmd.system.load("d", opts={"x": True})

    modulecmd.system.save_collection("foo")
    modulecmd.system.restore_collection("foo")

    modulecmd.system.add_to_loaded_collection("c")
    modulecmd.system.pop_from_loaded_collection("a")
    with pytest.raises(modulecmd.error.ModuleNotFoundError):
        modulecmd.system.add_to_loaded_collection("baz")
    with pytest.raises(Exception):
        modulecmd.system.pop_from_loaded_collection("baz")


def test_collection_bad(tmpdir):
    # nonexistent file: okay
    f = tmpdir.join("collections.json")
    collections = modulecmd.collection.Collections(f.strpath)

    # empty file: okay
    f = tmpdir.join("collections.json")
    f.write("{}")
    collections = modulecmd.collection.Collections(f.strpath)

    # existing file: okay
    f = tmpdir.join("collections.json")
    f.write('{"Version": [1,0], "Collections": []}')
    collections = modulecmd.collection.Collections(f.strpath)

    # badly formatted file: not okay
    f = tmpdir.join("f.json")
    f.write('{"Version": [1,0], "Collections": ["default":]}')
    try:
        from json.decoder import JSONDecodeError as error_type
    except ImportError:
        error_type = ValueError
    with pytest.raises(error_type):
        collections = modulecmd.collection.Collections(f.strpath)
        collections.data


def test_collection_read(modules, mock_modulepath):
    mock_modulepath(modules.path)
    a = modulecmd.system.load("a")
    b = modulecmd.system.load("b")
    modulecmd.system.save_collection(modulecmd.names.default_user_collection)
    assert modulecmd.collection.contains(modulecmd.names.default_user_collection)
    x = modulecmd.collection.get(modulecmd.names.default_user_collection)
    filename = modulecmd.collection.collections.file
    collection = modulecmd.collection.Collections(filename)
    default = collection.get(modulecmd.names.default_user_collection)
    default2 = modulecmd.collection.get(modulecmd.names.default_user_collection)
    assert len(default) == len(default2)
    for i in range(len(default)):
        assert default[i][0] == default2[i][0]
        assert default[i][1] == default2[i][1]
