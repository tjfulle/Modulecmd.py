import os
import pytest

import pymod.mc
import pymod.paths
import pymod.error
import pymod.environ
import pymod.collection


@pytest.fixture(scope="function", autouse=True)
def collection(tmpdir):
    assert pymod.collection.version() == (1, 0), "Wrong collection version!"
    real_collection = pymod.collection.collections
    filename = os.path.join(tmpdir.strpath, "collections.json")
    pymod.collection.collections = pymod.collection.Collections(filename)
    yield tmpdir.strpath
    pymod.collection.collections = real_collection


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
    a = pymod.mc.load("a")
    b = pymod.mc.load("b")
    pymod.mc.collection.save(pymod.names.default_user_collection)
    assert pymod.collection.contains(pymod.names.default_user_collection)
    x = pymod.collection.get(pymod.names.default_user_collection)
    assert len(x) == 1
    assert len(x[0]) == 2
    assert len(x[0][1]) == 2
    assert x[0][0] == pymod.modulepath._path.path[0].path
    coll = x[0][1]
    assert coll[0]["fullname"] == "a"
    assert coll[1]["fullname"] == "b"
    s = pymod.collection.avail()
    # None show up available since the default does not show avail
    assert not s.split()


def test_collection_named(modules, mock_modulepath):

    mock_modulepath(modules.path)
    a = pymod.mc.load("a")
    b = pymod.mc.load("b")
    c = pymod.mc.load("c")
    d = pymod.mc.load("d", opts={"x": True})

    pymod.mc.collection.save("foo")
    assert pymod.collection.contains("foo")
    x = pymod.collection.get("foo")
    assert len(x) == 2

    assert len(x[0]) == 2
    assert len(x[0][1]) == 2
    assert x[0][0] == pymod.modulepath._path.path[0].path

    coll = x[0][1]
    assert coll[0]["fullname"] == "a"
    assert coll[1]["fullname"] == "b"

    assert len(x[1]) == 2
    assert len(x[1][1]) == 2
    assert x[1][0] == pymod.modulepath._path.path[1].path

    coll = x[1][1]
    assert coll[0]["fullname"] == "c"
    assert coll[1]["fullname"] == "d"

    s = pymod.collection.avail().split("\n")[1].strip()
    assert s == "foo"

    s = pymod.collection.show("foo")

    pymod.mc.purge()
    pymod.mc.collection.restore("foo")
    for x in "abcd":
        assert pymod.modulepath.get(x) is not None

    pymod.mc.purge()

    # remove a module
    f = os.path.join(pymod.modulepath._path.path[0].path, "a.py")
    os.remove(f)
    with pytest.raises(pymod.error.CollectionModuleNotFoundError):
        pymod.mc.collection.restore("foo")

    pymod.collection.remove("foo")
    assert not pymod.collection.contains("foo")

    with pytest.raises(pymod.error.CollectionNotFoundError):
        pymod.mc.collection.restore("foo")


def test_collection_add_pop(modules, mock_modulepath):
    mock_modulepath(modules.path)
    a = pymod.mc.load("a")
    b = pymod.mc.load("b")
    d = pymod.mc.load("d", opts={"x": True})

    pymod.mc.collection.save("foo")
    pymod.mc.collection.restore("foo")

    pymod.mc.collection.add_to_loaded_collection("c")
    pymod.mc.collection.pop_from_loaded_collection("a")
    with pytest.raises(pymod.error.ModuleNotFoundError):
        pymod.mc.collection.add_to_loaded_collection("baz")
    with pytest.raises(Exception):
        pymod.mc.collection.pop_from_loaded_collection("baz")


def test_collection_bad(tmpdir):
    # nonexistent file: okay
    f = tmpdir.join("collections.json")
    collections = pymod.collection.Collections(f.strpath)

    # empty file: okay
    f = tmpdir.join("collections.json")
    f.write("{}")
    collections = pymod.collection.Collections(f.strpath)

    # existing file: okay
    f = tmpdir.join("collections.json")
    f.write('{"Version": [1,0], "Collections": []}')
    collections = pymod.collection.Collections(f.strpath)

    # badly formatted file: not okay
    f = tmpdir.join("f.json")
    f.write('{"Version": [1,0], "Collections": ["default":]}')
    try:
        from json.decoder import JSONDecodeError as error_type
    except ImportError:
        error_type = ValueError
    with pytest.raises(error_type):
        collections = pymod.collection.Collections(f.strpath)
        collections.data


def test_collection_read(modules, mock_modulepath):
    mock_modulepath(modules.path)
    a = pymod.mc.load("a")
    b = pymod.mc.load("b")
    pymod.mc.collection.save(pymod.names.default_user_collection)
    assert pymod.collection.contains(pymod.names.default_user_collection)
    x = pymod.collection.get(pymod.names.default_user_collection)
    filename = pymod.collection.collections.filename
    collection = pymod.collection.Collections(filename)
    default = collection.get(pymod.names.default_user_collection)
    default2 = pymod.collection.get(pymod.names.default_user_collection)
    assert len(default) == len(default2)
    for i in range(len(default)):
        assert default[i][0] == default2[i][0]
        assert default[i][1] == default2[i][1]
