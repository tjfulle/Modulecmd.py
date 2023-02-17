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
    assert modulecmd.modulepath.find_modules(tmpdir.strpath) is None


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


def test_modulepath_discover_nvv(tmpdir):
    a = tmpdir.mkdir("a")
    # These next two will be skipped
    a.join("1.0.py").write("")
    a.join("2.0.py").write("")
    one = a.mkdir("1")
    one.join("1.0.py").write("")
    one.join("2.0.py").write("")
    modules = modulecmd.modulepath.find_modules(tmpdir.strpath)
    assert len(modules) == 4
    x = sorted([(_.name, _.version.string, _.variant.string) for _ in modules])
    print(x)
    assert x == [("a", "1", "1.0"), ("a", "1", "2.0"), ("a", "1.0", ""), ("a", "2.0", "")]


def test_modulepath_discover_bad_linked_default(tmpdir):
    a = tmpdir.mkdir("a")
    a.join("1.0.py").write("")
    a.join("2.0.py").write("")
    a.join("default").write("")
    assert (
        modulecmd.modulepath.pop_linked_default(
            a.strpath, ["1.0.py", "2.0.py", "default"]
        )
        is None
    )

    os.remove(a.join("default").strpath)
    tmpdir.join("foo").write("")
    os.symlink(tmpdir.join("foo").strpath, os.path.join(a.strpath, "default"))
    linked_real_dirname = os.path.dirname(
        os.path.realpath(os.path.join(a.strpath, "default"))
    )
    assert linked_real_dirname == os.path.realpath(tmpdir.strpath)
    assert (
        modulecmd.modulepath.pop_linked_default(
            a.strpath, ["1.0.py", "2.0.py", "default"]
        )
        is None
    )


def test_modulepath_discover_bad_versioned_default(tmpdir):
    a = tmpdir.mkdir("a")
    a.join(".version").write("")
    assert (
        modulecmd.modulepath.pop_versioned_default(a.strpath, [".version"]) is None
    )


def test_modulepath_discover_versioned_default(tmpdir):
    a = tmpdir.mkdir("a")
    a.join(".version").write('set ModulesVersion "1.0"')
    assert (
        modulecmd.modulepath.pop_versioned_default(a.strpath, [".version"]) is None
    )

    a.join("1.0").write("")
    assert modulecmd.modulepath.pop_versioned_default(
        a.strpath, ["1.0", ".version"]
    ) == os.path.join(a.strpath, "1.0")
