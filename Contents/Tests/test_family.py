import pytest
import os


import tools
from pymod.defaults import LM_KEY


class TestFamily(tools.TestBase):

    module_1 = """family('test_fam')\nsetenv('ENVAR_1', '1')\n"""
    module_2 = """family('test_fam')\nsetenv('ENVAR_2', '2')\n"""

    def write_modules(self, base):
        d1 = tools.t_make_temp_directory(self.datadir)
        tools.t_make_directory(os.path.join(d1, base))
        with open(os.path.join(d1, base, '1.0.py'), 'w') as fh:
            fh.write(self.module_1)
        with open(os.path.join(d1, base, '2.0.py'), 'w') as fh:
            fh.write(self.module_2)
        return d1

    @pytest.mark.unit
    def test_family_load_1(self):
        family = 'compiler'
        name = 'ucc'
        version = '1.2'
        class M: pass
        mc = tools.t_controller(modulepath='')
        filename = os.path.join('', name, version + '.py')
        module = M()
        module.filename = filename;
        module.name = name
        module.version = version
        mc.family('load', family, module)
        assert mc.environ['MODULE_FAMILY_COMPILER'] == name
        assert mc.environ['MODULE_FAMILY_COMPILER_VERSION'] == version

    @pytest.mark.mf
    @pytest.mark.unit
    def test_mf_family_unload(self):
        family = 'compiler'
        name = 'ucc'
        version = '2.0'
        mc = tools.t_controller(modulepath='',
                                MODULE_FAMILY_COMPILER='ucc',
                                MODULE_FAMILY_UCC_VERSION='2.0')
        class M: pass
        filename = os.path.join('', name, version + '.py')
        module = M()
        module.filename = filename;
        module.name = name
        module.version = version
        mc.family('unload', family, module)
        assert mc['MODULE_FAMILY_COMPILER'] is None
        assert mc['MODULE_FAMILY_COMPILER_VERSION'] is None

    @pytest.mark.sandbox
    def test_exec_family_load_AB(self):

        d1 = tools.t_make_temp_directory(self.datadir)

        nameA, nameB = 'A/1.0', 'B/1.0'

        fA = os.path.join(d1, nameA + '.py')
        tools.t_make_directory(os.path.dirname(fA))
        with open(fA, 'w') as fh:
            fh.write("family('XYZ')\nsetenv('ENVAR_1', 'A')\n")

        fB = os.path.join(d1, nameB + '.py')
        tools.t_make_directory(os.path.dirname(fB))
        with open(fB, 'w') as fh:
            fh.write("family('XYZ')\nsetenv('ENVAR_1', 'B')\n")

        mc = tools.t_controller(modulepath=d1)

        mc.load('A')
        assert mc['MODULE_FAMILY_XYZ'] == 'A'
        assert mc['MODULE_FAMILY_XYZ_VERSION'] == '1.0'
        assert mc['ENVAR_1'] == 'A'

        assert 'A/1.0' in mc[LM_KEY]
        assert 'B/1.0' not in mc[LM_KEY]

        module = mc.modulepath.get_module_by_filename(fB)
        mc.execmodule('load', module)

        x = mc.m_state_changed.get('FamilyChange')
        assert x is not None
        assert x[0][0] == 'XYZ'
        mc.report_changed_module_state()

    @pytest.mark.sandbox
    def test_exec_family_impl_load(self):
        d1 = tools.t_make_temp_directory(self.datadir)
        tools.t_touch(os.path.join(d1, 'b/1.0.py'))
        tools.t_touch(os.path.join(d1, 'b/2.0.py'))
        mc = tools.t_controller(modulepath=d1)
        mc.load('b/1.0')
        assert 'b/1.0' in mc[LM_KEY]
        assert 'b/2.0' not in mc[LM_KEY]
        mc.load('b/2.0')
        assert 'b/1.0' not in mc[LM_KEY]
        assert 'b/2.0' in mc[LM_KEY]

    @pytest.mark.sandbox
    def test_exec_family_load_2(self):
        d1 = self.write_modules('a')
        d2 = self.write_modules('d')
        mc = tools.t_controller(modulepath=':'.join((d1,d2)))
        mc.load('a/1.0')
        assert mc['MODULE_FAMILY_TEST_FAM'] == 'a'
        assert mc['MODULE_FAMILY_TEST_FAM_VERSION'] == '1.0'
        assert mc['ENVAR_1'] == '1'
        assert 'a/1.0' in mc[LM_KEY]
        assert 'a/2.0' not in mc[LM_KEY]
        assert 'd/1.0' not in mc[LM_KEY]
        assert 'd/2.0' not in mc[LM_KEY]
        mc.load('a/2.0')
        assert mc['MODULE_FAMILY_TEST_FAM'] == 'a'
        assert mc['MODULE_FAMILY_TEST_FAM_VERSION'] == '2.0'
        assert mc['ENVAR_1'] is None
        assert mc['ENVAR_2'] == '2'
        assert 'a/1.0' not in mc[LM_KEY]
        assert 'a/2.0' in mc[LM_KEY]
        assert 'd/1.0' not in mc[LM_KEY]
        assert 'd/2.0' not in mc[LM_KEY]
        mc.load('d/1.0')
        assert 'a/1.0' not in mc[LM_KEY]
        assert 'a/2.0' not in mc[LM_KEY]
        assert 'd/1.0' in mc[LM_KEY]
        assert 'd/2.0' not in mc[LM_KEY]
        assert mc['MODULE_FAMILY_TEST_FAM'] == 'd'
        assert mc['MODULE_FAMILY_TEST_FAM_VERSION'] == '1.0'
        mc.load('d/2.0')
        assert 'a/1.0' not in mc[LM_KEY]
        assert 'a/2.0' not in mc[LM_KEY]
        assert 'd/1.0' not in mc[LM_KEY]
        assert 'd/2.0' in mc[LM_KEY]
        assert mc['MODULE_FAMILY_TEST_FAM'] == 'd'
        assert mc['MODULE_FAMILY_TEST_FAM_VERSION'] == '2.0'

