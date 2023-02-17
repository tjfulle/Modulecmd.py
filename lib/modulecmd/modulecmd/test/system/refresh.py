import modulecmd.system
import modulecmd.environ


def test_mc_refresh(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write('setenv("a", "a")\n')
    tmpdir.join("b.py").write('setenv("b", "b")\nload("c")\n')
    tmpdir.join("c.py").write('setenv("c", "c")\nload("d")\n')
    tmpdir.join("d.py").write('setenv("d", "d")\n')
    mock_modulepath(tmpdir.strpath)

    a = modulecmd.system.load("a")
    b = modulecmd.system.load("b")
    assert modulecmd.environ.get("a") == "a"
    assert modulecmd.environ.get("b") == "b"
    assert modulecmd.environ.get("c") == "c"
    assert modulecmd.environ.get("d") == "d"
    modulecmd.system.refresh()
    assert modulecmd.environ.get("a") == "a"
    assert modulecmd.environ.get("b") == "b"
    assert modulecmd.environ.get("c") == "c"
    assert modulecmd.environ.get("d") == "d"
    # Reference count should not change
    assert a.refcount == 1
    assert a.refcount == 1
