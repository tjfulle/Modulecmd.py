import os
import pytest
import modulecmd.paths
import modulecmd.system
import modulecmd.module
import modulecmd.modulepath
from modulecmd.util.itertools import groupby


basic_py_module = """\
setenv(self.name, '1')
prepend_path('PREPEND', self.version.string)
prepend_path('APPEND', self.version.string)
"""

basic_tcl_module = """\
#%Module1.0
setenv {0} 1
prepend-path PREPEND {1}
append-path APPEND {1}
"""


@pytest.fixture()
def dirtrees(tmpdir):
    one = tmpdir.mkdir("1")
    one.join("a.py").write(basic_py_module)
    one.join("b.py").write(basic_py_module)

    py = one.mkdir("py")
    py.join("1.0.0.py").write(basic_py_module)
    py.join("2.0.0.py").write(basic_py_module)
    py.join("3.0.0.py").write(basic_py_module)
    default = py.join("default")
    default.mksymlinkto(py.join("2.0.0.py"))

    tcl = one.mkdir("tcl")
    tcl.join("1.0.0").write(basic_tcl_module.format("tcl", "1.0.0"))
    tcl.join("2.0.0").write(basic_tcl_module.format("tcl", "2.0.0"))
    tcl.join("3.0.0").write(basic_tcl_module.format("tcl", "3.0.0"))
    tcl.join(".version").write('set ModulesVersion "1.0.0"')

    ucc = one.mkdir("ucc")
    ucc.join("1.0.0.py").write(basic_py_module)
    ucc.join("2.0.0.py").write(basic_py_module)

    two = tmpdir.mkdir("2")
    ucc = two.mkdir("ucc")
    ucc.join("1.0.0.py").write(basic_py_module)
    ucc.join("4.0.0.py").write(basic_py_module)

    xxx = two.mkdir("xxx")
    xxx.join("1.0.0.py").write(basic_py_module)

    # 2 defaults
    X = one.mkdir("X")
    X.join("2.0.0.py").write(basic_py_module)
    X.join("3.0.0").write(basic_tcl_module.format("X", "3.0.0"))
    X.join(".version").write('set ModulesVersion "3.0.0"')
    default = X.join("default")
    default.mksymlinkto(X.join("2.0.0.py"))

    return tmpdir


def test_modulepath_two_defaults(tmpdir, mock_modulepath):
    one = tmpdir.mkdir("1")
    X = one.mkdir("X")
    f2 = X.join("2.0.0.py")
    f2.write(basic_py_module)
    f3 = X.join("3.0.0")
    f3.write(basic_tcl_module.format("X", "3.0.0"))
    X.join(".version").write('set ModulesVersion "3.0.0"')
    default = X.join("default")
    default.mksymlinkto(f2)
    mock_modulepath(one.strpath)
    x = modulecmd.modulepath.get("X")
    assert x.version == "2.0.0"
    assert isinstance(x, modulecmd.module.PyModule)


def test_modulepath_bad_default(tmpdir, mock_modulepath):
    a = tmpdir.mkdir("a")
    a.join("3.0.0").write(basic_tcl_module.format("a", "3.0.0"))
    a.join("4.0.0").write(basic_tcl_module.format("a", "4.0.0"))
    a.join(".version").write('set ModulesVersion "5.0.0"')
    mock_modulepath(tmpdir.strpath)
    ma = modulecmd.modulepath.get("a")
    assert ma.version.string == "4.0.0"
    assert isinstance(ma, modulecmd.module.TclModule)


def test_modulepath_available_1(dirtrees, mock_modulepath):
    dirname = dirtrees.join("1").strpath
    mock_modulepath(dirname)
    assert modulecmd.modulepath.size() == 1
    modules = modulecmd.modulepath.get(dirname)

    grouped = dict(groupby(modules, lambda x: x.name))

    a = grouped.pop("a")
    assert len(a) == 1
    assert not a[0].is_default
    assert isinstance(a[0], modulecmd.module.PyModule)

    b = grouped.pop("b")
    assert len(b) == 1
    assert not b[0].is_default
    assert isinstance(b[0], modulecmd.module.PyModule)

    py = grouped.pop("py")
    assert len(py) == 3
    for m in py:
        assert m.is_default if m.fullname == "py/2.0.0" else not m.is_default
        assert isinstance(m, modulecmd.module.PyModule)

    tcl = grouped.pop("tcl")
    assert len(tcl) == 3
    for m in tcl:
        assert m.is_default if m.fullname == "tcl/1.0.0" else not m.is_default
        assert isinstance(m, modulecmd.module.TclModule)

    ucc = grouped.pop("ucc")
    assert len(ucc) == 2
    for m in ucc:
        assert m.is_default if m.fullname == "ucc/2.0.0" else not m.is_default
        assert isinstance(m, modulecmd.module.PyModule)


def test_modulepath_get(dirtrees, mock_modulepath):
    d1 = dirtrees.join("1").strpath
    mock_modulepath(d1)

    module = modulecmd.modulepath.get("a")
    assert module.fullname == "a"
    assert isinstance(module, modulecmd.module.PyModule)
    assert module.filename == os.path.join(d1, module.fullname + ".py")

    module = modulecmd.modulepath.get("b")
    assert module.fullname == "b"
    assert isinstance(module, modulecmd.module.PyModule)
    assert module.filename == os.path.join(d1, module.fullname + ".py")

    module = modulecmd.modulepath.get("py")
    assert module.fullname == "py/2.0.0"
    assert isinstance(module, modulecmd.module.PyModule)
    assert module.filename == os.path.join(d1, module.fullname + ".py")

    module = modulecmd.modulepath.get("tcl")
    assert module.fullname == "tcl/1.0.0"
    assert isinstance(module, modulecmd.module.TclModule)
    assert module.filename == os.path.join(d1, module.fullname)

    module = modulecmd.modulepath.get("ucc")
    assert module.fullname == "ucc/2.0.0"
    assert isinstance(module, modulecmd.module.PyModule)
    assert module.filename == os.path.join(d1, module.fullname + ".py")

    module = modulecmd.modulepath.get("ucc/1.0.0")
    assert module.fullname == "ucc/1.0.0"
    assert isinstance(module, modulecmd.module.PyModule)
    assert module.filename == os.path.join(d1, module.fullname + ".py")

    modules = modulecmd.modulepath.get(d1)
    assert len(modules) == 12

    d2 = dirtrees.join("2").strpath
    modulecmd.modulepath.prepend_path(d2)

    # should grab d2, since it is higher in priority
    module = modulecmd.modulepath.get("ucc/1.0.0")
    assert module.fullname == "ucc/1.0.0"
    assert isinstance(module, modulecmd.module.PyModule)
    assert module.filename == os.path.join(d2, module.fullname + ".py")

    # use more of d1, to get its module
    f = os.path.join(d1, "ucc/1.0.0")[-15:]
    module = modulecmd.modulepath.get(f)
    assert module.fullname == "ucc/1.0.0"
    assert isinstance(module, modulecmd.module.PyModule)
    assert module.filename == os.path.join(d1, module.fullname + ".py")


def test_modulepath_append_path(dirtrees, mock_modulepath):

    d1 = dirtrees.join("1").strpath
    mock_modulepath(d1)

    module = modulecmd.modulepath.get("ucc/1.0.0")
    assert module.fullname == "ucc/1.0.0"
    assert module.filename == os.path.join(d1, module.fullname + ".py")

    module = modulecmd.modulepath.get("ucc")
    assert module.fullname == "ucc/2.0.0"
    assert module.filename == os.path.join(d1, module.fullname + ".py")

    d2 = dirtrees.join("2").strpath
    d2_modules = modulecmd.modulepath.append_path(d2)
    assert len(d2_modules) != 0
    x = modulecmd.modulepath.append_path(d2)
    assert x is None  # d2 already on modulepath and we are appending

    module = modulecmd.modulepath.get("ucc/1.0.0")
    assert module.fullname == "ucc/1.0.0"
    assert module.filename == os.path.join(d1, module.fullname + ".py")

    module = modulecmd.modulepath.get("ucc")
    assert module.fullname == "ucc/4.0.0"
    assert module.filename == os.path.join(d2, module.fullname + ".py")

    xxx = modulecmd.system.load("xxx")

    removed = modulecmd.modulepath.remove_path(d2)
    assert len(removed) == 3
    removed_full_names = [m.fullname for m in removed]
    assert "ucc/1.0.0" in removed_full_names
    assert "ucc/4.0.0" in removed_full_names
    assert "xxx/1.0.0" in removed_full_names

    module = modulecmd.modulepath.get("ucc")
    assert module.fullname == "ucc/2.0.0"
    assert module.filename == os.path.join(d1, module.fullname + ".py")

    # No modules
    dirtrees.mkdir("FOO")
    x = modulecmd.modulepath.append_path(dirtrees.join("FOO").strpath)
    assert x is None


def test_modulepath_prepend_path(dirtrees, mock_modulepath):
    d1 = dirtrees.join("1").strpath
    mock_modulepath(d1)

    module = modulecmd.modulepath.get("ucc/1.0.0")
    assert module.fullname == "ucc/1.0.0"
    assert module.filename == os.path.join(d1, module.fullname + ".py")

    module = modulecmd.modulepath.get("ucc")
    assert module.fullname == "ucc/2.0.0"
    assert module.filename == os.path.join(d1, module.fullname + ".py")

    d2 = dirtrees.join("2").strpath
    modulecmd.modulepath.prepend_path(d2)

    module = modulecmd.modulepath.get("ucc/1.0.0")
    assert module.fullname == "ucc/1.0.0"
    assert module.filename == os.path.join(d2, module.fullname + ".py")

    module = modulecmd.modulepath.get("ucc")
    assert module.fullname == "ucc/4.0.0"
    assert module.filename == os.path.join(d2, module.fullname + ".py")

    removed = modulecmd.modulepath.remove_path(d2)
    assert len(removed) == 3
    removed_full_names = [m.fullname for m in removed]
    assert "ucc/1.0.0" in removed_full_names
    assert "ucc/4.0.0" in removed_full_names
    assert "xxx/1.0.0" in removed_full_names

    module = modulecmd.modulepath.get("ucc/1.0.0")
    assert module.fullname == "ucc/1.0.0"
    assert module.filename == os.path.join(d1, module.fullname + ".py")

    module = modulecmd.modulepath.get("ucc")
    assert module.fullname == "ucc/2.0.0"
    assert module.filename == os.path.join(d1, module.fullname + ".py")

    modulecmd.modulepath.prepend_path(d1)
    module = modulecmd.modulepath.get("ucc/1.0.0")
    assert module.fullname == "ucc/1.0.0"
    assert module.filename == os.path.join(d1, module.fullname + ".py")

    dirtrees.mkdir("FOO")
    a = modulecmd.modulepath.prepend_path(dirtrees.join("FOO").strpath)
    assert a is None


def test_modulepath_auto_bump(dirtrees, mock_modulepath):

    d1 = dirtrees.join("1").strpath
    d2 = dirtrees.join("2").strpath
    mock_modulepath(d1)

    m1 = modulecmd.modulepath.get("ucc")
    assert m1.version == "2.0.0"

    modules = modulecmd.modulepath.prepend_path(d2)

    m2 = modulecmd.modulepath.get("ucc")
    assert m2.version == "4.0.0"

    for path in modulecmd.modulepath.path():
        assert path is not None

    modulecmd.modulepath.clear()


def test_modulepath_traverse(dirtrees, mock_modulepath):

    d1 = dirtrees.join("1").strpath
    d2 = dirtrees.join("2").strpath
    mock_modulepath([d1, d2])
    i = 0
    for path in modulecmd.modulepath.path():
        if i == 0:
            assert path == d1
            i += 1
        elif i == 1:
            assert path == d2
            i += 1
        else:
            assert False, "Should never get here"


def test_modulepath_dirname_does_not_exist(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write("")
    mock_modulepath(tmpdir.strpath)
    modules = modulecmd.modulepath.append_path("A/FAKE/PATH")
    assert modules is None
    bumped = modulecmd.modulepath.prepend_path("A/FAKE/PATH")
    assert bumped is None


def test_modulepath_no_value(tmpdir, mock_modulepath):
    is_in = modulecmd.names.modulepath in os.environ
    mock_modulepath([])
    assert modulecmd.modulepath._path.value is None

    a = tmpdir.mkdir("a")
    a.join("a.py").write("")
    b = tmpdir.mkdir("b")
    b.join("b.py").write("")

    modulecmd.modulepath.append_path(a.strpath)
    assert modulecmd.modulepath._path.value == a.strpath

    modulecmd.modulepath.prepend_path(b.strpath)
    assert modulecmd.modulepath._path.value == os.pathsep.join([b.strpath, a.strpath])

    modulecmd.modulepath.remove_path(a.strpath)
    assert modulecmd.modulepath._path.value == b.strpath

    modulecmd.modulepath.remove_path(b.strpath)
    assert modulecmd.modulepath._path.value is None

    env = modulecmd.environ.copy()
    if is_in:
        assert env[modulecmd.names.modulepath] is None
