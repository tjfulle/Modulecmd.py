import pymod.mc
import pymod.environ


def test_mc_opts_preserve(tmpdir, mock_modulepath):
    tmpdir.join('a.py').write(
        'add_option("+x")\n'
        'opts = parse_opts()\n'
        'self.x = opts.x')
    mock_modulepath(tmpdir.strpath)
    a = pymod.mc.load('a', opts=['+x=spam'])
    assert a.x == 'spam'
    assert a.opts == ['+x=spam']

    modules = pymod.mc.get_loaded_modules()
    assert len(modules) == 1
    assert modules[0].filename == a.filename
    assert modules[0].opts == ['+x=spam']
    pymod.mc.unload('a')
    a = pymod.mc.load('a')
    assert a.x is None
