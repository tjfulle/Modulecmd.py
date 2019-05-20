import pytest

from pymod.main import PymodCommand


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds
    one = tmpdir.mkdir('1')
    one.join('a.py').write(m.setenv('a'))
    ns = namespace()
    ns.one = one.strpath
    return ns


def test_command_more(modules_path, mock_modulepath):
    more = PymodCommand('more')
    mock_modulepath(modules_path.one)
    more('a')
