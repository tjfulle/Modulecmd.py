import os
import pytest
import modulecmd.system
from modulecmd.callback import get_callback


def test_callback_utility_check_output():
    check_output = get_callback("check_output")
    check_output(None, None, "ls -l")


def test_callback_utility_colorize():
    colorize = get_callback("colorize")
    s = "@r{RED}"
    red_s = colorize(None, None, s)


def test_callback_utility_listdir(tmpdir):
    listdir = get_callback("listdir")
    check_output = get_callback("check_output")
    tmpdir.join("foo").write("")
    tmpdir.join("baz").write("")
    files = sorted(listdir(None, None, tmpdir.strpath))
    assert len(files) == 2
    assert [os.path.basename(f) for f in files] == ["baz", "foo"]

    out = check_output(None, None, "ls -l {0}".format(tmpdir.strpath))
    out_l = [
        x.split()[-1] for x in out.split("\n") if x.split() and "rw" in x.split()[0]
    ]
    assert out_l == ["baz", "foo"]

    files = listdir(None, None, tmpdir.strpath, key=lambda x: not x.endswith("baz"))
    assert len(files) == 1
    assert [os.path.basename(f) for f in files] == ["foo"]


def test_callback_utility_mkdirp(tmpdir):
    mkdirp = get_callback("mkdirp")
    d = os.path.join(tmpdir.strpath, "foo", "baz")
    mkdirp(None, None, d)
    assert os.path.isdir(d)


def test_callback_utility_which():
    which = get_callback("which")
    ls = which(None, None, "ls")
    assert os.path.exists(ls)


def test_callback_logging(tmpdir, mock_modulepath):
    tmpdir.join("info.py").write('log_info("spam")')
    tmpdir.join("warning.py").write('log_warning("spam")')
    tmpdir.join("error.py").write('log_error("spam")')
    mock_modulepath(tmpdir.strpath)
    modulecmd.system.load("info")
    modulecmd.system.load("warning")
    try:
        modulecmd.system.show("error")
        assert False, "Should have died"
    except:
        pass


def test_callback_mode(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write('assert mode() == "load"')
    mock_modulepath(tmpdir.strpath)
    modulecmd.system.load("a")


def test_callback_get_hostname(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write("host = get_hostname()")
    mock_modulepath(tmpdir.strpath)
    modulecmd.system.load("a")


@pytest.mark.unit
def test_callback_execute(tmpdir):
    execute = get_callback("execute")
    tmpdir.join("foobar").write("")
    f = os.path.join(tmpdir.strpath, "foobar")
    command = "touch {0}".format(f)
    execute(None, modulecmd.modes.load, command)
    assert os.path.isfile(f)


def test_callback_execute_2(tmpdir, mock_modulepath):
    f = os.path.join(tmpdir.strpath, "foobar")
    tmpdir.join("a.py").write("execute('touch {0}', when=mode()=='load')".format(f))
    mock_modulepath(tmpdir.strpath)
    modulecmd.system.load("a")
    assert os.path.isfile(f)
    os.remove(f)
    modulecmd.system.unload("a")
    assert not os.path.isfile(f)


def test_callback_chdir(tmpdir, mock_modulepath):
    f = os.path.join(tmpdir.strpath, "foobar")
    d = tmpdir.mkdir("foo").strpath
    tmpdir.join("a.py").write("chdir('{0}')".format(d))
    tmpdir.join("b.py").write("chdir('a_fake_dir')")
    mock_modulepath(tmpdir.strpath)
    modulecmd.system.load("a")
    with pytest.raises(SystemExit):
        modulecmd.system.load("b")
    s = modulecmd.environ.format_output()
    x = [_.strip() for _ in s.split("\n") if _.split()][-1]
    assert x == "cd {0};".format(d)
