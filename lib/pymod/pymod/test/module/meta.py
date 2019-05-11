import os
import pytest
from pymod.module.meta import (
    MetaData, MetaDataValueError, MetaDataUnknownFieldsError)


def test_module_meta_1(tmpdir):
    meta = MetaData()
    tmpdir.join('f.py').write('# pymod: enable_if=False, do_not_register=True')
    f = os.path.join(tmpdir.strpath, 'f.py')
    meta.parse(f)
    assert meta.is_enabled is False
    assert meta.do_not_register is True


def test_module_meta_2(tmpdir):
    meta = MetaData()
    tmpdir.join('f.py').write('# pymod: enable_if= not False, do_not_register=not None')
    f = os.path.join(tmpdir.strpath, 'f.py')
    meta.parse(f)
    assert meta.is_enabled is True
    assert meta.do_not_register is True


def test_module_meta_3(tmpdir):
    meta = MetaData()
    tmpdir.join('f.py').write('# pymod: enable_if= os.path.isdir(os.getcwd()), do_not_register=bool(sys.platform)')
    f = os.path.join(tmpdir.strpath, 'f.py')
    meta.parse(f)
    assert meta.is_enabled is True
    assert meta.do_not_register is True


def test_module_meta_4(tmpdir):
    meta = MetaData()
    with pytest.raises(MetaDataValueError):
        tmpdir.join('f.py').write('# pymod: enable_if= bad, do_not_register=bool(sys.platform)')
        f = os.path.join(tmpdir.strpath, 'f.py')
        meta.parse(f)


def test_module_meta_5(tmpdir):
    meta = MetaData()
    with pytest.raises(MetaDataUnknownFieldsError):
        tmpdir.join('f.py').write('# pymod: a = True')
        f = os.path.join(tmpdir.strpath, 'f.py')
        meta.parse(f)
