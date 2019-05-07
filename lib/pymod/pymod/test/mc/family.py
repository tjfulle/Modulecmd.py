import os
import pytest

import pymod.mc
import pymod.modes
import pymod.names
import pymod.environ
import pymod.modulepath

@pytest.fixture()
def modules_path(tmpdir):
    basic_py_module = """\
family('XYZ')
setenv('ENVAR_1', self.name)
setenv('ENVAR_2', self.version.string)"""
    a = tmpdir.mkdir('A')
    a.join('1.0.py').write(basic_py_module)
    a.join('2.0.py').write(basic_py_module)
    b = tmpdir.mkdir('B')
    b.join('1.0.py').write(basic_py_module)
    b.join('2.0.py').write(basic_py_module)
    return tmpdir.strpath


@pytest.mark.unit
def test_family_load_1(mock_module):
    family = 'compiler'
    module = mock_module('ucc', '1.2', 'ucc/1.2.py')
    pymod.mc.family(pymod.modes.load, module, 'compiler')
    assert pymod.environ.environ['MODULE_FAMILY_COMPILER'] == 'ucc'
    assert pymod.environ.environ['MODULE_FAMILY_COMPILER_VERSION'] == '1.2'


@pytest.mark.mf
@pytest.mark.unit
def test_family_unload_1(mock_module):
    module = mock_module('ucc', '2.0', 'ucc/2.0.py')
    pymod.environ.set('MODULE_FAMILY_COMPILER', 'ucc')
    pymod.environ.set('MODULE_FAMILY_UCC_VERSION', '2.0')
    pymod.mc.family(pymod.modes.unload, module, 'compiler')
    assert pymod.environ.environ['MODULE_FAMILY_COMPILER'] is None
    assert pymod.environ.environ['MODULE_FAMILY_COMPILER_VERSION'] is None


@pytest.mark.sandbox
def test_family_xyz(modules_path, mock_modulepath, get_loaded_modules):

    def standard_assertions(module):
        name_key = pymod.names.family_name('xyz')
        ver_key = pymod.names.family_version('xyz')
        assert pymod.environ.environ[name_key] == module.name
        assert pymod.environ.environ[ver_key] == module.version.string
        assert pymod.environ.environ['ENVAR_1'] == module.name
        assert pymod.environ.environ['ENVAR_2'] == module.version.string
        loaded_modules = get_loaded_modules()
        for key in ('A', 'B'):
            for ver in ('1.0', '2.0'):
                id = '{}/{}'.format(key, ver)
                if id == module.fullname:
                    assert id in loaded_modules
                else:
                    assert id not in loaded_modules

    mp = mock_modulepath(modules_path)

    a1 = pymod.modulepath.get('A/1.0')
    assert a1 is not None
    pymod.mc.execmodule(a1, pymod.modes.load)
    standard_assertions(a1)

    a2 = pymod.modulepath.get('A/2.0')
    assert a2 is not None
    pymod.mc.execmodule(a2, pymod.modes.load)
    standard_assertions(a2)

    old, new = pymod.mc._mc._swapped_on_family_update[0]
    assert old.name == 'A'
    assert new.name == 'A'

    b1 = pymod.modulepath.get('B/1.0')
    assert b1 is not None
    pymod.mc.execmodule(b1, pymod.modes.load)
    standard_assertions(b1)

    old, new = pymod.mc._mc._swapped_on_family_update[1]
    assert old.name == 'A'
    assert new.name == 'B'

    b2 = pymod.modulepath.get('B/2.0')
    assert b2 is not None
    pymod.mc.execmodule(b2, pymod.modes.load)
    standard_assertions(b2)

    old, new = pymod.mc._mc._swapped_on_family_update[2]
    assert old.name == 'B'
    assert new.name == 'B'
