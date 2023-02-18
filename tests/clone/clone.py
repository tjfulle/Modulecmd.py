import os
import pytest

import modulecmd.system
import modulecmd.paths
import modulecmd.environ
import modulecmd.clone


def test_clone_named(tmpdir, mock_modulepath):

    tmpdir.join("a.py").write("")
    tmpdir.join("b.py").write("")
    tmpdir.join("c.py").write("")
    tmpdir.join("d.py").write("")

    mock_modulepath(tmpdir.strpath)

    a = modulecmd.system.load("a")
    b = modulecmd.system.load("b")
    c = modulecmd.system.load("c")
    d = modulecmd.system.load("d")

    modulecmd.system.save_clone("foo")
    x = modulecmd.clone.get("foo")
    assert x is not None

    modulecmd.system.purge()
    modulecmd.system.restore_clone("foo")
    for x in "abcd":
        assert modulecmd.modulepath.get(x) is not None

    modulecmd.system.purge()

    # remove a module
    f = os.path.join(modulecmd.modulepath.path()[0], "a.py")
    os.remove(f)
    with pytest.raises(modulecmd.error.CloneModuleNotFoundError):
        modulecmd.system.restore_clone("foo")

    modulecmd.clone.remove("foo")
    x = modulecmd.clone.get("foo")
    assert x is None

    with pytest.raises(modulecmd.error.CloneDoesNotExistError):
        modulecmd.system.restore_clone("foo")


def test_clone_bad(tmpdir):
    # nonexistent file: okay
    f = tmpdir.join("clones.json")
    clones = modulecmd.clone.Clones(f.strpath)

    # empty file: okay
    f = tmpdir.join("clones.json")
    f.write("{}")
    clones = modulecmd.clone.Clones(f.strpath)

    # existing file: okay
    f = tmpdir.join("clones.json")
    f.write('{"foo": {}}')
    clones = modulecmd.clone.Clones(f.strpath)

    # badly formatted file: not okay
    f = tmpdir.join("clones.json")
    f.write("{")
    try:
        from json.decoder import JSONDecodeError as error_type
    except ImportError:
        error_type = ValueError
    with pytest.raises(error_type):
        clones = modulecmd.clone.Clones(f.strpath)
        clones.data
