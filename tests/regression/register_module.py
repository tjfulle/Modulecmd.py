import pytest
import modulecmd.system
import modulecmd.modulepath


def test_regression_register(tmpdir, mock_modulepath):
    # Module refcount was being updated *after* it was archived, so it was
    # effectively not updated :(
    tmpdir.join("a.py").write("")
    mock_modulepath(tmpdir.strpath)

    a = modulecmd.modulepath.get("a")
    modulecmd.system.register_module(a)

    loaded_modules = modulecmd.system.loaded_modules()
    assert len(loaded_modules) == 1
    assert loaded_modules[0].refcount == 1

    with pytest.raises(modulecmd.system.ModuleRegisteredError):
        modulecmd.system.register_module(a)

    modulecmd.system.unregister_module(a)
    with pytest.raises(modulecmd.system.ModuleNotRegisteredError):
        modulecmd.system.unregister_module(a)
