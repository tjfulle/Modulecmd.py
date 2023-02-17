import os
import pytest

import modulecmd.system
import modulecmd.paths
import modulecmd.environ
from modulecmd.main import PymodCommand
from modulecmd.error import CloneDoesNotExistError


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


def test_command_clone(modules_path, mock_modulepath):

    mock_modulepath(modules_path.path)
    clone = PymodCommand("clone")
    a = modulecmd.system.load("a")
    b = modulecmd.system.load("b")
    c = modulecmd.system.load("c")
    d = modulecmd.system.load("d")

    clone("save", "foo")

    modulecmd.system.purge()
    assert not a.is_loaded
    assert not b.is_loaded
    assert not c.is_loaded
    assert not d.is_loaded

    clone("restore", "foo")
    for x in "abcd":
        m = modulecmd.modulepath.get(x)
        assert m.is_loaded

    modulecmd.system.purge()

    clone("remove", "foo")
    assert modulecmd.clone.get("foo") is None


def test_command_restore_clone_bad(modules_path, mock_modulepath):
    clone = PymodCommand("clone")
    with pytest.raises(CloneDoesNotExistError):
        clone("restore", "fake")


def test_command_clone2(modules_path, mock_modulepath):

    mock_modulepath(modules_path.path)
    clone = PymodCommand("clone")
    a = modulecmd.system.load("a")
    b = modulecmd.system.load("b")
    c = modulecmd.system.load("c")
    d = modulecmd.system.load("d")

    clone("save", "foo")

    modulecmd.system.purge()
    assert not a.is_loaded
    assert not b.is_loaded
    assert not c.is_loaded
    assert not d.is_loaded

    clone("restore", "foo")
    for x in "abcd":
        m = modulecmd.modulepath.get(x)
        assert m.is_loaded

    clone("avail")
    clone("avail", "-t")
    clone("avail", "--terse")
