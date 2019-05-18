import pytest
import pymod.mc
import pymod.error
from pymod.module import module

def test_mc_register_1(tmpdir, mock_modulepath):
    tmpdir.join('a.py').write('')
    a = module(tmpdir.strpath, 'a.py')
    mp = mock_modulepath(tmpdir.strpath)
    pymod.mc.register_module(a)
    assert a.filename in pymod.mc._mc.loaded_module_files()


def test_mc_register_2(tmpdir, mock_modulepath):
    value = pymod.config.get('skip_add_devpack')
    pymod.config.set('skip_add_devpack', True)
    tmpdir.join('devpack.py').write('')
    mp = mock_modulepath(tmpdir.strpath)
    m = module(tmpdir.strpath, 'devpack.py')
    print(m.modulepath)
    print(tmpdir.strpath)
    print(pymod.modulepath.path())
    pymod.mc.register_module(m)
    assert m.filename not in pymod.mc._mc.loaded_module_files()
    pymod.config.set('skip_add_devpack', value)


def test_mc_register_3(tmpdir):
    tmpdir.join('a.py').write('')
    a = module(tmpdir.strpath, 'a.py')
    with pytest.raises(pymod.error.InconsistentModuleStateError):
        pymod.mc.register_module(a)


def test_mc_decrement_refcount(tmpdir, mock_modulepath):
    tmpdir.join('a.py').write('')
    a = module(tmpdir.strpath, 'a.py')
    count = pymod.mc._mc.get_lm_refcount().get(a.fullname)
    assert count is None
    mp = mock_modulepath(tmpdir.strpath)
    pymod.mc.load('a')
    count = pymod.mc._mc.get_lm_refcount()[a.fullname]
    assert count == 1
    pymod.mc.increment_refcount(a)
    count = pymod.mc._mc.get_lm_refcount()[a.fullname]
    assert count == 2
    pymod.mc.decrement_refcount(a)
    pymod.mc.unload('a')
    count = pymod.mc._mc.get_lm_refcount().get(a.fullname)
    assert count is None
