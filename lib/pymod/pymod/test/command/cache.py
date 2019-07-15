from pymod.main import PymodCommand

def test_command_cache(tmpdir, mock_modulepath):
    tmpdir.join('a.py').write('')
    mock_modulepath(tmpdir.strpath)
    cache = PymodCommand('cache')
    cache('build')
    cache('remove')
