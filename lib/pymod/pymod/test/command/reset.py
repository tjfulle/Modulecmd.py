from pymod.main import PymodCommand


def test_command_reset(tmpdir, mock_modulepath):
    init = PymodCommand('init')
    reset = PymodCommand('reset')
    tmpdir.join('a.py')
    init('-p', tmpdir.strpath)
    reset()
