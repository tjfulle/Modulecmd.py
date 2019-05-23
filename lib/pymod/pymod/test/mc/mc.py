import pymod.mc
import pymod.names
import pymod.environ
import pymod.modulepath


def test_mc_cellar(tmpdir, mock_modulepath):
    assert pymod.mc._mc._loaded_modules is None

    # Need to write our own
    names = 'abc'
    for name in names:
        tmpdir.join(name+'.py').write('')
    mock_modulepath(tmpdir.strpath)

    lm_cellar = []
    for name in names:
        m = pymod.modulepath.get(name)
        lm_cellar.append(dict(fullname=m.fullname, filename=m.filename,
                              family=m.family, opts=m.opts, acquired_as=m.acquired_as))
    pymod.environ.set_list(pymod.names.loaded_module_cellar, lm_cellar)
    loaded_modules = pymod.mc.get_loaded_modules()
    loaded_module_names = ''.join(m.name for m in loaded_modules)
    assert loaded_module_names == names
