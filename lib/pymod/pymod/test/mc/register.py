import pytest
import pymod.mc
import pymod.error
import pymod.modulepath
from pymod.module import module

def test_mc_register_1(tmpdir, mock_modulepath):
    tmpdir.join('a.py').write('')
    mock_modulepath(tmpdir.strpath)
    a = pymod.modulepath.get('a')
    pymod.mc.register_module(a)
    assert a.filename in [_.filename for _ in pymod.mc.get_loaded_modules()]


def test_mc_register_2(tmpdir, mock_modulepath):
    value = pymod.config.get('skip_add_devpack')
    pymod.config.set('skip_add_devpack', True)
    tmpdir.join('devpack.py').write('')
    mock_modulepath(tmpdir.strpath)
    m = module(tmpdir.strpath, 'devpack.py')
    pymod.mc.register_module(m)
    assert m.filename not in [_.filename for _ in pymod.mc.get_loaded_modules()]
    pymod.config.set('skip_add_devpack', value)


def test_mc_register_3(tmpdir):
    tmpdir.join('a.py').write('')
    a = module(tmpdir.strpath, 'a.py')
    with pytest.raises(pymod.error.InconsistentModuleStateError):
        pymod.mc.register_module(a)


def test_mc_refcount_decrement(tmpdir, mock_modulepath):
    tmpdir.join('a.py').write('')
    mock_modulepath(tmpdir.strpath)
    a = pymod.modulepath.get('a')
    assert a.refcount == 0

    pymod.mc.load('a')
    assert a.refcount == 1

    pymod.mc.increment_refcount(a)
    assert a.refcount == 2

    pymod.mc.decrement_refcount(a)
    pymod.mc.unload('a')
    assert a.refcount == 0


def test_mc_refcount(tmpdir, mock_modulepath):
    tmpdir.join('a.py').write('')
    a = module(tmpdir.strpath, 'a.py')
    pymod.mc.increment_refcount(a)
    assert a.refcount == 1

    pymod.mc.increment_refcount(a)
    assert a.refcount == 2

    pymod.mc.decrement_refcount(a)
    assert a.refcount == 1

    pymod.mc.decrement_refcount(a)
    assert a.refcount == 0

    with pytest.raises(ValueError):
        # This will put the reference count < 0
        pymod.mc.decrement_refcount(a)
