import os
import pytest
import pymod.module


@pytest.fixture()
def basic_python_module(tmpdir):
    tmpdir.join("a.py").write('add_option("foo")\n' 'setenv("a", "a")')
    m = pymod.module.module(tmpdir.strpath, "a.py")
    return m


@pytest.fixture()
def basic_tcl_module(tmpdir):
    tmpdir.join("a").write('#%Module1.0\nsetenv a "a"')
    m = pymod.module.module(tmpdir.strpath, "a")
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


def test_module_format_dl_status(basic_python_module):
    m = basic_python_module
    pymod.environ.set(pymod.names.loaded_modules, m.fullname)
    m.format_dl_status()
    m.is_default = True
    m.format_dl_status()


def test_module_parts(tmpdir):
    d = tmpdir
    s = "abcde"
    for x in s:
        d = d.mkdir(x)

    with pytest.raises(IOError):
        pymod.module.Module(tmpdir.strpath, *list(s))

    f = d.join("f")
    f.write("")
    parts = list(s + "f")
    ff = os.path.join(tmpdir.strpath, *parts)
    assert f.strpath == ff
    assert os.path.isfile(ff)
    with pytest.raises(ValueError):
        pymod.module.Module(tmpdir.strpath, *parts)


def test_module_basic(tmpdir):
    one = tmpdir.mkdir("1")
    one.join("a").write("")
    a = pymod.module.Module(one.strpath, "a")
    assert a.is_enabled
    a.format_help()


def test_module_bad_opts(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write('add_option("x")\nassert opts.x=="foo"')
    mp = mock_modulepath(tmpdir.strpath)
    a = pymod.mc.load("a", opts={"x": "foo"})
    assert a.kwargv == {"x": "foo"}
    pymod.mc.unload("a")

    with pytest.raises(SystemExit):
        pymod.mc.load("a", opts={"y": True})
