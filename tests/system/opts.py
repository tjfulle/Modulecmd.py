import modulecmd.system
import modulecmd.environ


def test_mc_opts_preserve(tmpdir, mock_modulepath):
    tmpdir.join("a.py").write('add_option("x")\n' "self.x = opts.x")
    mock_modulepath(tmpdir.strpath)
    a = modulecmd.system.load("a", opts={"x": "spam"})
    assert a.x == "spam"
    assert a.parse_opts().as_dict() == {"x": "spam"}

    modules = modulecmd.system.loaded_modules()
    assert len(modules) == 1
    assert modules[0].filename == a.filename
    assert modules[0].parse_opts().as_dict() == {"x": "spam"}
    modulecmd.system.unload("a")
    a = modulecmd.system.load("a")
    assert a.x is None
