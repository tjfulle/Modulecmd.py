from pymod.main import PymodCommand


def test_command_list(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write("")
    tmpdir.join("b.py").write('add_option("x")')
    tmpdir.join("c.py").write("")
    load = PymodCommand("load")
    list = PymodCommand("list")
    mock_modulepath(tmpdir.strpath)
    list()
    load("a")
    load("b", "x=foo")
    load("c")
    list()
    list("a")  # regular expression
    list("-c")
    list("-t")
