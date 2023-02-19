import os
import pytest
import modulecmd.system
import modulecmd.module


@pytest.fixture()
def basic_python_module(tmpdir):
    tmpdir.join("a.py").write('add_option("foo")\n' 'setenv("a", "a")')
    m = modulecmd.module.factory(tmpdir.strpath, "a.py")
    return m


@pytest.fixture()
def basic_tcl_module(tmpdir):
    tmpdir.join("a").write('#%Module1.0\nsetenv a "a"')
    m = modulecmd.module.factory(tmpdir.strpath, "a")
    return m


def test_module_attrs(basic_python_module):
    m = basic_python_module
    m.opts = {"foo": True}
    assert not m.is_loaded
    assert not m.is_hidden


def test_module_whatis(basic_python_module):
    m = basic_python_module
    m.add_option("foo")
    m.add_option("bar", help="a bar")
    m.set_whatis(
        short_description="SHORT DESCRIPTION",
        configure_options="BUILD CONFIG OPTIONS",
        version="1.0",
        foo="baz",
    )
    m.format_whatis()


def test_module_parts(tmpdir):
    d = tmpdir
    parts = list("abcde")
    for x in parts:
        d = d.mkdir(x)
    path = os.path.join(*parts)

    with pytest.raises(IOError):
        modulecmd.module.Module(tmpdir.strpath, path)

    f = d.join("f")
    f.write("")
    parts.append("f")
    ff = os.path.join(tmpdir.strpath, *parts)
    assert f.strpath == ff
    assert os.path.isfile(ff)
    path = os.path.join(*parts)
    m = modulecmd.module.Module(tmpdir.strpath, path)
    assert m.version.major == "f"
    assert m.version.minor is None
    assert m.version.patch is None


def test_module_basic(tmpdir):
    one = tmpdir.mkdir("1")
    one.join("a").write("")
    a = modulecmd.module.Module(one.strpath, "a")
    assert a.is_enabled
    a.format_help()


def test_module_bad_opts(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write('add_option("x")\nassert opts.x=="foo"')
    mp = mock_modulepath(tmpdir.strpath)
    a = modulecmd.system.load("a", opts={"x": "foo"})
    assert a.kwargv == {"x": "foo"}
    modulecmd.system.unload("a")

    with pytest.raises(SystemExit):
        modulecmd.system.load("a", opts={"y": True})
