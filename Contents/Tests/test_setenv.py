import os
import pytest

import tools

class TestSetenv(tools.TestBase):


    def write_modules_a_b(self):
        d1 = tools.t_make_temp_directory(self.datadir)
        with open(os.path.join(d1, 'a.py'), 'w') as fh:
            fh.write("setenv('test_envar_key', 'test_envar_val')")
        with open(os.path.join(d1, 'b.py'), 'w') as fh:
            fh.write("unsetenv('test_envar_key')")
        return d1

    @pytest.mark.unit
    def test_setenv_load_modulepath(self):
        mc = tools.t_controller(modulepath='')
        try:
            mc.setenv(MP_KEY, 'A/PATH')
            raise Exception('MODULEPATH cannot be set!')
        except:
            pass

    @pytest.mark.unit
    def test_unsetenv_load_modulepath(self):
        mc = tools.t_controller(modulepath='')
        try:
            mc.unsetenv(MP_KEY)
            raise Exception('MODULEPATH cannot be set!')
        except:
            pass

    @pytest.mark.unit
    def test_setenv(self):
        mc = tools.t_controller(modulepath='')
        mc.setenv('envar', 'value')
        assert mc.get('envar') == 'value'

    @pytest.mark.unit
    def test_unsetenv(self):
        mc = tools.t_controller(modulepath='', envar='value')
        mc.unsetenv('envar')
        assert mc.get('envar') is None

    @pytest.mark.sandbox
    def test_exec_setenv_mode_load(self):
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1)
        mc.load('a')
        assert mc.get('test_envar_key') == 'test_envar_val'

    @pytest.mark.sandbox
    def test_exec_setenv_mode_unload(self):
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1, test_envar_key='test_envar_val')
        mc.load('a')
        assert mc.get('test_envar_key') == 'test_envar_val'
        mc.unload('a')
        assert mc.get('test_envar_key') is None

    @pytest.mark.sandbox
    def test_exec_unsetenv_mode_load(self):
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1, test_envar_key='test_envar_val')
        mc.load('b')
        assert mc.get('test_envar_key') is None

    @pytest.mark.sandbox
    def test_exec_unsetenv_mode_unload(self):
        # unsetenv is a nonop in unload mode
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1, test_envar_key='test_envar_val')
        mc.unload('b')
        assert mc.get('test_envar_key') == 'test_envar_val'

