import pytest

from pymod.main import PymodCommand


def test_command_help_module(tmpdir, modulecmds, mock_modulepath):
    m = modulecmds
    help = PymodCommand('help')
    tmpdir.join('a.py').write(m.help('HELP A'))
    mock_modulepath(tmpdir.strpath)
    help('a')


def test_command_help_h():
    help = PymodCommand('help')
    with pytest.raises(SystemExit):
        help('help', '-h')


def test_command_help_2():
    help = PymodCommand('help')
    help()
