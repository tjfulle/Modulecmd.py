import pytest
import modulecmd.cache


def test_cache_build(tmpdir, mock_modulepath):
    assert not modulecmd.cache.modified()
    tmpdir.join("a.py").write("")
    mock_modulepath(tmpdir.strpath)
    assert modulecmd.cache.modified()
    modulecmd.cache.build()


def test_cache_load(tmpdir, mock_modulepath):
    assert not modulecmd.cache.modified()
    tmpdir.join("a.py").write("")
    mock_modulepath(tmpdir.strpath)
    assert modulecmd.cache.modified()
    filename = modulecmd.cache.cache.file
    modulecmd.cache.write()
    new_cache = modulecmd.cache.Cache(filename)
    from_new_cache = new_cache.get(modulecmd.names.modulepath, tmpdir.strpath)
    from_old_cache = modulecmd.cache.get(modulecmd.names.modulepath, tmpdir.strpath)
    assert len(from_new_cache) == len(from_old_cache)


def test_cache_remove(tmpdir, mock_modulepath):
    assert not modulecmd.cache.modified()
    tmpdir.join("a.py").write("")
    mock_modulepath(tmpdir.strpath)
    assert modulecmd.cache.modified()
    # this will create the cache
    modulecmd.modulepath.avail()
    modulecmd.cache.remove()
