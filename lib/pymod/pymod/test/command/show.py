import pytest
from pymod.main import PymodCommand
from pymod.error import ModuleNotFoundError


def test_command_show(tmpdir, mock_modulepath):
    tmpdir.join('a.py').write('')
    show = PymodCommand('show')
    mock_modulepath(tmpdir.strpath)
    show('a', '+x')
    with pytest.raises(ModuleNotFoundError):
        show('fake')
    with pytest.raises(ValueError):
        # need module for options
        show('+x')
