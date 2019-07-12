import pytest
import pymod.modulepath

@pytest.mark.skip(reason="Takes too long")
def test_modulepath_cache_refresh(tmpdir, mock_modulepath):
    tmpdir.join('a.py').write('')
    mock_modulepath(tmpdir.strpath)
    # this will create the cache
    pymod.modulepath.avail()
    pymod.modulepath.refresh_cache()

def test_modulepath_cache_load(tmpdir, mock_modulepath):
    tmpdir.join('a.py').write('')
    mock_modulepath(tmpdir.strpath)
    # this will create the cache
    pymod.modulepath.avail()
    filename = pymod.modulepath._cache.filename
    new_cache = pymod.modulepath.Cache(filename)
    from_new_cache = new_cache.get(tmpdir.strpath)
    from_old_cache = pymod.modulepath.get_from_cache(tmpdir.strpath)
    assert len(from_new_cache) == len(from_old_cache)

def test_modulepath_cache_remove(tmpdir, mock_modulepath):
    tmpdir.join('a.py').write('')
    mock_modulepath(tmpdir.strpath)
    # this will create the cache
    pymod.modulepath.avail()
    pymod.modulepath.remove_cache()
