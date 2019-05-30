import pytest
import pymod.mc
import pymod.modulepath


def test_regression_register(tmpdir, mock_modulepath):
    # Module refcount was being updated *after* it was archived, so it was
    # effectively not updated :(
    tmpdir.join('a.py').write('')
    mock_modulepath(tmpdir.strpath)

    a = pymod.modulepath.get('a')
    pymod.mc.register_module(a)

    loaded_modules = pymod.mc.get_loaded_modules()
    assert len(loaded_modules) == 1
    assert loaded_modules[0].refcount == 1

    with pytest.raises(pymod.mc._mc.ModuleRegisteredError):
        pymod.mc.register_module(a)

    pymod.mc.unregister_module(a)
    with pytest.raises(pymod.mc._mc.ModuleNotRegisteredError):
        pymod.mc.unregister_module(a)
