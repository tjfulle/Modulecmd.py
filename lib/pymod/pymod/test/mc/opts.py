import pymod.mc
import pymod.environ


def test_mc_module_opts(tmpdir, mock_modulepath):
    tmpdir.join('a.py').write(
        'add_option("+x")\n'
        'opts = parse_opts()\n'
        'self.x = opts.x')
    mock_modulepath(tmpdir.strpath)
    a = pymod.mc.load('a', opts=['+x=spam'])
    assert a.x == 'spam'

    # make sure get_loaded_modules resets opts if needed
    a._opts = None
    modules = pymod.mc.get_loaded_modules()
    assert len(modules) == 1
    assert modules[0] == a
    assert a.opts == ['+x=spam']
    pymod.mc.unload('a')
    a = pymod.mc.load('a')
    assert a.x is None
