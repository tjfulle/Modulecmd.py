import os
import pytest
import modulecmd.modulepath


def test_modulepath_discover_root(mock_modulepath):
    assert modulecmd.modulepath.find_modules("/") is None
    p = mock_modulepath("/")
    assert not p.path
    assert modulecmd.modulepath.find_modules("fake") is None


def test_modulepath_discover_noexist():
    assert modulecmd.modulepath.find_modules("a fake dir") is None


def test_modulepath_discover_nomodules(tmpdir):
    assert modulecmd.modulepath.find_modules(tmpdir.strpath) == []


def test_modulepath_discover_bad_marked_default(tmpdir):
    # Won't respect module linked to default, since these are unversioned
    # modules
    tmpdir.join("a.py").write("")
    tmpdir.join("b.py").write("")
    os.symlink(tmpdir.join("b.py").strpath, os.path.join(tmpdir.strpath, "default"))
    modules = modulecmd.modulepath.find_modules(tmpdir.strpath)
    assert len(modules) == 2
    names = sorted([x.name for x in modules])
    assert names == ["a", "b"]


def test_modulepath_discover_n2v(tmpdir):
    a = tmpdir.mkdir("a")
    # These next two will be skipped
    a.join("1.0.py").write("")
    a.join("2.0.py").write("")
    one = a.mkdir("1")
    one.join("1.0.py").write("")
    one.join("2.0.py").write("")
    modules = modulecmd.modulepath.find_modules(tmpdir.strpath)
    assert len(modules) == 4
    x = sorted([(_.name, _.version.string) for _ in modules])
    assert x == [("a", "1.0"), ("a", "2.0"), ("a/1", "1.0"), ("a/1", "2.0")]


def test_modulepath_discover_nvv(tmpdir):
    a = tmpdir.mkdir("a")
    # These next two will be skipped
    a.join(".version").write("")
    a.join("1.0.py").write("")
    a.join("2.0.py").write("")
    one = a.mkdir("1")
    one.join("1.0.py").write("")
    one.join("2.0.py").write("")
    modules = modulecmd.modulepath.find_modules(tmpdir.strpath)
    assert len(modules) == 4
    x = sorted([(_.name, _.version.string) for _ in modules])
    assert x == [('a', '1.0'), ('a', '1/1.0'), ('a', '1/2.0'), ('a', '2.0')]
