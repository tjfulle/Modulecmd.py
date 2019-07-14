import pytest
import pymod.cache

@pytest.mark.skip(reason="Takes too long")
def test_cache_refresh(tmpdir, mock_modulepath):
    tmpdir.join('a.py').write('')
    mock_modulepath(tmpdir.strpath)
    # this will create the cache
    pymod.modulepath.avail()
    pymod.cache.refresh_cache()

def test_cache_load(tmpdir, mock_modulepath):
    tmpdir.join('a.py').write('')
    mock_modulepath(tmpdir.strpath)
    # this will create the cache
    pymod.modulepath.avail()
    filename = pymod.cache._cache.filename
    new_cache = pymod.cache.Cache(filename)
    from_new_cache = new_cache.get(tmpdir.strpath)
    from_old_cache = pymod.cache.get(tmpdir.strpath)
    assert len(from_new_cache) == len(from_old_cache)

def test_cache_remove(tmpdir, mock_modulepath):
    tmpdir.join('a.py').write('')
    mock_modulepath(tmpdir.strpath)
    # this will create the cache
    pymod.modulepath.avail()
    pymod.cache.remove()
