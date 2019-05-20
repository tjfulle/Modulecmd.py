from pymod.main import PymodCommand


def test_command_help_module(tmpdir, modulecmds, mock_modulepath):
    m = modulecmds
    init = PymodCommand('init')
    tmpdir.join('a.py').write(m.help('HELP A'))
    init('-p', tmpdir.strpath)
