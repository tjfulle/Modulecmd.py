import os
import pytest

import pymod.mc
import pymod.environ
from pymod.main import PymodCommand
from pymod.error import ModuleNotFoundError


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds
    tmpdir.join('a.py').write(
        'add_option("+x", action="store_true")'
        '\nsetenv("a", "a")')
    return tmpdir.strpath


def test_mc_show(modules_path, mock_modulepath):
    mp = mock_modulepath(modules_path)
    show = PymodCommand('show')
    show('a')

    show('a', '+x')

    with pytest.raises(ModuleNotFoundError):
        show('fake')
