import pymod.mc
import pymod.environ


def test_mc_refresh(tmpdir, mock_modulepath):
    tmpdir.join('a.py').write('setenv("a", "a")\n')
    tmpdir.join('b.py').write('setenv("b", "b")\nload("c")\n')
    tmpdir.join('c.py').write('setenv("c", "c")\nload("d")\n')
    tmpdir.join('d.py').write('setenv("d", "d")\n')
    mock_modulepath(tmpdir.strpath)

    a = pymod.mc.load('a')
    b = pymod.mc.load('b')
    assert pymod.environ.get('a') == 'a'
    assert pymod.environ.get('b') == 'b'
    assert pymod.environ.get('c') == 'c'
    assert pymod.environ.get('d') == 'd'
    pymod.mc.refresh()
    assert pymod.environ.get('a') == 'a'
    assert pymod.environ.get('b') == 'b'
    assert pymod.environ.get('c') == 'c'
    assert pymod.environ.get('d') == 'd'
    # Reference count should not change
    assert a.refcount == 1
    assert a.refcount == 1
