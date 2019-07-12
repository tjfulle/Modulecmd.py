import os
import pytest
import pymod.discover

def test_modulepath_discover_root(mock_modulepath):
    with pytest.raises(ValueError):
        modules = pymod.discover.find_modules('/')
    with pytest.raises(ValueError):
        mock_modulepath('/')
    assert pymod.discover.find_modules('fake') is None


@pytest.mark.skip(reason="It takes too long")
def test_modulepath_discover_cache_refresh(tmpdir, mock_modulepath):
    tmpdir.join('a.py').write('')
    mock_modulepath(tmpdir.strpath)
    # this will create the cache
    pymod.modulepath.avail()
    pymod.discover.refresh_cache()

def test_modulepath_discover_cache_reload(tmpdir, mock_modulepath):
    tmpdir.join('a.py').write('')
    mock_modulepath(tmpdir.strpath)
    # this will create the cache
    pymod.modulepath.avail()
    pymod.discover.reload_cache()

def test_modulepath_discover_cache_remove(tmpdir, mock_modulepath):
    tmpdir.join('a.py').write('')
    mock_modulepath(tmpdir.strpath)
    # this will create the cache
    pymod.modulepath.avail()
    pymod.discover.remove_cache()
