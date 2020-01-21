import os
import pytest
import pymod.modulepath


def test_modulepath_discover_root(mock_modulepath):
    with pytest.raises(ValueError):
        modules = pymod.modulepath.discover.find_modules("/")
    with pytest.raises(ValueError):
        mock_modulepath("/")
    assert pymod.modulepath.discover.find_modules("fake") is None


def test_modulepath_discover_noexist():
    assert pymod.modulepath.discover.find_modules("a fake dir") is None


def test_modulepath_discover_nomodules(tmpdir):
    assert pymod.modulepath.discover.find_modules(tmpdir.strpath) is None


def test_modulepath_discover_bad_marked_default(tmpdir):
    # Won't respect module linked to default, since these are unversioned
    # modules
    tmpdir.join("a.py").write("")
    tmpdir.join("b.py").write("")
    os.symlink(tmpdir.join("b.py").strpath, os.path.join(tmpdir.strpath, "default"))
    modules = pymod.modulepath.discover.find_modules(tmpdir.strpath)
    assert len(modules) == 2
    names = sorted([x.name for x in modules])
    assert names == ["a", "b"]


def test_modulepath_discover_bad_n(tmpdir):
    # The name 'f' does not exist
    assert pymod.modulepath.discover.find_modules_n(tmpdir.strpath, ["f"]) == []


def test_modulepath_discover_bad_nv(tmpdir):
    a = tmpdir.mkdir("a")
    b = a.mkdir("b")
    a.join("1.0.py").write("")
    a.join("2.0.py").write("")
    with pytest.raises(ValueError):
        pymod.modulepath.discover.find_modules_nv(tmpdir.strpath, "a")


def test_modulepath_discover_bad_nvv(tmpdir):
    a = tmpdir.mkdir("a")
    one = a.mkdir("1")
    one.join("1.0.py").write("")
    one.join("2.0.py").write("")
    one.mkdir("b")
    assert pymod.modulepath.discover.find_modules_nvv(tmpdir.strpath, "a", "1") is None


def test_modulepath_discover_skip_nvv(tmpdir):
    a = tmpdir.mkdir("a")
    # These next two will be skipped
    a.join("1.0.py").write("")
    a.join("2.0.py").write("")
    one = a.mkdir("1")
    one.join("1.0.py").write("")
    one.join("2.0.py").write("")
    modules = pymod.modulepath.discover.find_modules(tmpdir.strpath)
    assert len(modules) == 2
    x = sorted([(_.name, _.version.string, _.variant.string) for _ in modules])
    assert x == [("a", "1", "1.0"), ("a", "1", "2.0")]


def test_modulepath_discover_bad_linked_default(tmpdir):
    a = tmpdir.mkdir("a")
    a.join("1.0.py").write("")
    a.join("2.0.py").write("")
    a.join("default").write("")
    assert (
        pymod.modulepath.discover.pop_linked_default(
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
        pymod.modulepath.discover.pop_linked_default(
            a.strpath, ["1.0.py", "2.0.py", "default"]
        )
        is None
    )


def test_modulepath_discover_bad_versioned_default(tmpdir):
    a = tmpdir.mkdir("a")
    a.join(".version").write("")
    assert (
        pymod.modulepath.discover.pop_versioned_default(a.strpath, [".version"]) is None
    )


def test_modulepath_discover_versioned_default(tmpdir):
    a = tmpdir.mkdir("a")
    a.join(".version").write('set ModulesVersion "1.0"')
    assert (
        pymod.modulepath.discover.pop_versioned_default(a.strpath, [".version"]) is None
    )

    a.join("1.0").write("")
    assert pymod.modulepath.discover.pop_versioned_default(
        a.strpath, ["1.0", ".version"]
    ) == os.path.join(a.strpath, "1.0")
