import os
import pytest

import pymod.mc
import pymod.paths
import pymod.environ
import pymod.clone


def test_clone_named(tmpdir, mock_modulepath):

    tmpdir.join("a.py").write("")
    tmpdir.join("b.py").write("")
    tmpdir.join("c.py").write("")
    tmpdir.join("d.py").write("")

    mock_modulepath(tmpdir.strpath)

    a = pymod.mc.load("a")
    b = pymod.mc.load("b")
    c = pymod.mc.load("c")
    d = pymod.mc.load("d")

    pymod.mc.clone.save("foo")
    x = pymod.clone.get("foo")
    assert x is not None

    s = pymod.clone.avail().split("\n")[1].strip()
    assert s == "foo"

    pymod.mc.purge()
    pymod.mc.clone.restore("foo")
    for x in "abcd":
        assert pymod.modulepath.get(x) is not None

    pymod.mc.purge()

    # remove a module
    f = os.path.join(pymod.modulepath._path.path[0].path, "a.py")
    os.remove(f)
    with pytest.raises(pymod.error.CloneModuleNotFoundError):
        pymod.mc.clone.restore("foo")

    pymod.clone.remove("foo")
    x = pymod.clone.get("foo")
    assert x is None

    with pytest.raises(pymod.error.CloneDoesNotExistError):
        pymod.mc.clone.restore("foo")


def test_clone_bad(tmpdir):
    # nonexistent file: okay
    f = tmpdir.join("clones.json")
    clones = pymod.clone.Clones(f.strpath)

    # empty file: okay
    f = tmpdir.join("clones.json")
    f.write("{}")
    clones = pymod.clone.Clones(f.strpath)

    # existing file: okay
    f = tmpdir.join("clones.json")
    f.write('{"foo": {}}')
    clones = pymod.clone.Clones(f.strpath)

    # badly formatted file: not okay
    f = tmpdir.join("clones.json")
    f.write("{")
    try:
        from json.decoder import JSONDecodeError as error_type
    except ImportError:
        error_type = ValueError
    with pytest.raises(error_type):
        clones = pymod.clone.Clones(f.strpath)
        clones.data
