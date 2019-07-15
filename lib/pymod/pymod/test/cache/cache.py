import pytest
import pymod.cache

def test_cache_build(tmpdir, mock_modulepath):
    assert not pymod.cache.modified()
    tmpdir.join('a.py').write('')
    mock_modulepath(tmpdir.strpath)
    assert pymod.cache.modified()
    pymod.cache.build()

def test_cache_load(tmpdir, mock_modulepath):
    assert not pymod.cache.modified()
    tmpdir.join('a.py').write('')
    mock_modulepath(tmpdir.strpath)
    assert pymod.cache.modified()
    filename = pymod.cache.cache.filename
    pymod.cache.write()
    new_cache = pymod.cache.Cache(filename)
    from_new_cache = new_cache.get(pymod.names.modulepath, tmpdir.strpath)
    from_old_cache = pymod.cache.get(pymod.names.modulepath, tmpdir.strpath)
    assert len(from_new_cache) == len(from_old_cache)

def test_cache_remove(tmpdir, mock_modulepath):
    assert not pymod.cache.modified()
    tmpdir.join('a.py').write('')
    mock_modulepath(tmpdir.strpath)
    assert pymod.cache.modified()
    # this will create the cache
    pymod.modulepath.avail()
    pymod.cache.remove()
