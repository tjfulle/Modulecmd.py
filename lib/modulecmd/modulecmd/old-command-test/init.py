from modulecmd.main import PymodCommand


def test_command_init(tmpdir, mock_modulepath):
    init = PymodCommand("init")
    tmpdir.join("a.py")
    init("-p", tmpdir.strpath)
