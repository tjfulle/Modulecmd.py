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
    tmpdir.join('b').write('#%Module1.0')
    return tmpdir.strpath
    return tmpdir.strpath


def test_mc_show(modules_path, mock_modulepath):
    mock_modulepath(modules_path)
    pymod.mc.show('a')

    pymod.mc.show('a', opts=['+x'])

    with pytest.raises(ModuleNotFoundError):
        pymod.mc.show('fake')


def test_mc_show_tcl(modules_path, mock_modulepath):
    mock_modulepath(modules_path)
    pymod.mc.show('b')
