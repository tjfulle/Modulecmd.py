import os
import pytest

import pymod.mc
import pymod.environ
from pymod.error import ModuleNotFoundError


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds
    tmpdir.join('a.py').write(
        'add_option("+x", action="store_true")'
        '\nsetenv("a", "a")')
    return tmpdir.strpath


@pytest.mark.unit
def test_mc_show(modules_path, mock_modulepath):
    """Just load and then unload a"""
    mp = mock_modulepath(modules_path)
    pymod.mc.show('a')

    pymod.mc.show('a', opts=['+x'])

    with pytest.raises(ModuleNotFoundError):
        pymod.mc.show('fake')
