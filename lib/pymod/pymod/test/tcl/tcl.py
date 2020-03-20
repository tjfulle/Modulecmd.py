import pytest

import pymod.names
import pymod.modes
import pymod.config
import pymod.module
import pymod.modulepath
from pymod.module.tcl2py import tcl2py

pytestmark = pytest.mark.skipif(not pymod.config.has_tclsh, reason="No tclsh")

py_content = '''\
whatis("""adds `.' to your PATH environment variable """)
append_path("path", "/b/path", sep=":")
prepend_path("path", "/a/path", sep=":")
setenv("foo","BAR")
set_alias("alias","BAZ")
'''


tcl_content = """\
#%Module1.0
proc ModulesHelp { } {
        global dotversion

        puts stderr "\tAdds `.' to your PATH environment variable"
        puts stderr "\n\tThis makes it easy to add the current working directory"
        puts stderr "\tto your PATH environment variable.  This allows you to"
        puts stderr "\trun executables in your current working directory"
        puts stderr "\twithout prepending ./ to the excutable name"
        puts stderr "\n\tVersion $dotversion\n"
}

module-whatis   "adds `.' to your PATH environment variable"

# for Tcl script use only
set     dotversion      3.2.10

append-path     path /b/path
prepend-path    path /a/path
setenv foo BAR
set-alias alias BAZ
"""


@pytest.fixture()
def tcl_module_path(tmpdir):

    d = tmpdir.mkdir("tcl2")
    p = d.join("1.0")
    p.write(tcl_content)

    tcl = tmpdir.mkdir("tcl")
    p = tcl.join("1.0")
    p.write(
        """\
#%Module1.0
append-path     path /b/path
prepend-path    path /a/path
setenv ENVAR tcl/1.0
set-alias foo BAR"""
    )

    a = tmpdir.mkdir("a")
    p = a.join("1.0")
    p.write(
        """\
#%Module1.0
append-path path  /c/path
setenv ENVAR a/1.0
set-alias foo BAZ"""
    )

    p = a.join("2.0")
    p.write(
        """\
#%Module1.0
append-path path  /d/path
setenv ENVAR a/2.0
set-alias foo SPAM"""
    )

    p = a.join(".version")
    p.write('set ModulesVersion "1.0"')

    return tmpdir.strpath


@pytest.mark.tcl
def test_tcl_tcl2py_1(tcl_module_path, mock_modulepath):
    mock_modulepath(tcl_module_path)
    module = pymod.modulepath.get("tcl2")
    assert isinstance(module, pymod.module.TclModule)
    assert module.version.string == "1.0"
    stdout = tcl2py(module, pymod.modes.load)
    try:
        stdout = stdout.decode("utf-8")
    except AttributeError:
        pass
    assert str(stdout) == str(py_content)


@pytest.mark.tcl
def test_tcl_tcl2py_2(tcl_module_path, mock_modulepath):
    mock_modulepath(tcl_module_path)
    pymod.environ.set(pymod.names.ld_library_path, "path_a")
    pymod.environ.set(pymod.names.ld_preload, "path_c")
    module = pymod.modulepath.get("tcl2")
    assert isinstance(module, pymod.module.TclModule)
    assert module.version.string == "1.0"
    stdout = tcl2py(module, pymod.modes.load)
    assert stdout == py_content


@pytest.mark.unit
@pytest.mark.tcl
def test_tcl_unit(tcl_module_path, mock_modulepath):
    mock_modulepath(tcl_module_path)

    tcl = pymod.modulepath.get("tcl")
    assert tcl is not None
    assert tcl.name == "tcl"
    assert tcl.fullname == "tcl/1.0"
    assert isinstance(tcl, pymod.module.TclModule)

    # version 1.0 should be the default
    a1 = pymod.modulepath.get("a")
    assert a1 is not None
    assert a1.name == "a"
    assert a1.fullname == "a/1.0", a1.fullname
    assert isinstance(a1, pymod.module.TclModule)

    a2 = pymod.modulepath.get("a/2.0")
    assert a2 is not None
    assert a2.name == "a"
    assert a2.fullname == "a/2.0"
    assert isinstance(a2, pymod.module.TclModule)

    pymod.mc.load_impl(tcl)
    assert pymod.environ.environ["path"] == "/a/path:/b/path"
    assert pymod.environ.environ["ENVAR"] == "tcl/1.0"
    assert pymod.environ.environ.aliases["foo"] == "BAR"

    pymod.mc.load_impl(a1)
    assert pymod.environ.environ["path"] == "/a/path:/b/path:/c/path"
    assert pymod.environ.environ["ENVAR"] == "a/1.0"
    assert pymod.environ.environ.aliases["foo"] == "BAZ"

    pymod.mc.load_impl(a2)
    assert pymod.environ.environ["path"] == "/a/path:/b/path:/d/path"
    assert pymod.environ.environ["ENVAR"] == "a/2.0"
    assert pymod.environ.environ.aliases["foo"] == "SPAM"


@pytest.mark.tcl
def test_tcl_break(tmpdir, mock_modulepath):
    f = tmpdir.join("f").write(
        """\
#%Module1.0
setenv foo BAR
break
setenv BAZ SPAM"""
    )
    mock_modulepath(tmpdir.strpath)
    m = pymod.mc.load("f")
    assert pymod.environ.get("foo") is None
    assert pymod.environ.get("BAZ") is None
    assert not m.is_loaded


@pytest.mark.tcl
def test_tcl_env(tmpdir, mock_modulepath):
    f = tmpdir.join("f").write(
        """\
#%Module1.0
if [info exists env(FOO)] {
  setenv BAZ $env(FOO)
} else {
  setenv BAZ SPAM
}
"""
    )
    mock_modulepath(tmpdir.strpath)
    pymod.environ.set("FOO", "BAR")
    m = pymod.mc.load("f")
    assert pymod.environ.get("BAZ") == "BAR"
    assert m.is_loaded
    pymod.mc.unload("f")

    pymod.environ.environ.pop("FOO")
    m = pymod.mc.load("f")
    assert pymod.environ.get("BAZ") == "SPAM"
    pymod.environ.environ.pop("BAZ")
    pymod.environ.environ.pop("FOO", None)


@pytest.mark.tcl
def test_tcl_env_break(tmpdir, mock_modulepath):
    f = tmpdir.join("f").write(
        """\
#%Module1.0
if { [info exists env(FOO)] } {
  break
} else {
  setenv BAZ SPAM
}
"""
    )
    mock_modulepath(tmpdir.strpath)

    pymod.environ.environ.pop("FOO", None)
    m = pymod.mc.load("f")
    assert pymod.environ.get("BAZ") == "SPAM"
    assert m.is_loaded
    pymod.mc.unload("f")

    pymod.environ.set("FOO", "BAR")
    pymod.environ.environ.pop("BAZ", None)
    m = pymod.mc.load("f")
    assert pymod.environ.get("BAZ") is None
    assert not m.is_loaded

    pymod.environ.environ.pop("FOO")


@pytest.mark.tcl
def test_tcl_env_break_neg(tmpdir, mock_modulepath):
    f = tmpdir.join("f").write(
        """\
#%Module1.0
if { ![info exists env(FOO)] } {
  setenv BAZ SPAM
} else {
  break
}
"""
    )
    mock_modulepath(tmpdir.strpath)

    pymod.environ.environ.pop("FOO", None)
    m = pymod.mc.load("f")
    assert pymod.environ.get("BAZ") == "SPAM"
    assert m.is_loaded
    pymod.mc.unload("f")

    pymod.environ.set("FOO", "BAR")
    pymod.environ.environ.pop("BAZ", None)
    m = pymod.mc.load("f")
    assert pymod.environ.get("BAZ") is None
    assert not m.is_loaded

    pymod.environ.environ.pop("FOO")


@pytest.mark.tcl
def test_tcl_continue(tmpdir, mock_modulepath):
    f = tmpdir.join("f").write(
        """\
#%Module1.0
setenv foo BAR
continue
setenv BAZ SPAM"""
    )
    mock_modulepath(tmpdir.strpath)
    m = pymod.mc.load("f")
    assert pymod.environ.get("foo") == "BAR"
    assert pymod.environ.get("BAZ") is None
    assert m.is_loaded
