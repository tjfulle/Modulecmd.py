import pytest
from modulecmd.main import PymodCommand


def test_command_avail(tmpdir, mock_modulepath):
    load = PymodCommand("load")
    avail = PymodCommand("avail")
    save = PymodCommand("save")

    # Build modules
    one = tmpdir.mkdir("1")
    one.join("a.py").write('setenv("a", "a")\n')
    one.join("b.py").write('setenv("b", "b")\nload("c")')
    one.join("c.py").write('setenv("c", "c")\nload("d")')
    one.join("d.py").write('setenv("d", "d")\nload("e")')
    one.join("e.py").write('setenv("e", "e")\n')

    two = tmpdir.mkdir("2")
    two.join("a.py").write('setenv("a", "a")\n')
    two.join("b.py").write('setenv("b", "b")\nload_first("c", "e", "d")')
    two.join("d.py").write('setenv("d", "c")\nadd_option("x")')
    two.join("g.py").write('setenv("g", "d")\nload_first("x", "y", "z", None)')

    mock_modulepath([one.strpath, two.strpath])
    load("a")
    load("b")
    load("c")
    load("d", "x=foo")
    save("foo")
    avail()
    avail("-t")
    avail("--terse")
    avail("a")  # regular expression
    avail("--terse", "a")  # regular expression

    avail("-a")
    avail("--terse", "-a")
    avail("--terse", "-a", "a")
