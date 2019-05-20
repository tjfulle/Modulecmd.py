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


def test_command_cat(modules_path, mock_modulepath):
    cat = PymodCommand('cat')
    mock_modulepath(modules_path.one)
    cat('a')

    with pytest.raises(Exception):
        cat('fake')
