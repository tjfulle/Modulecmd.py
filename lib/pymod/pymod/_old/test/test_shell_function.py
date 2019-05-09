import os
import pytest

import tools


class TestShellFunction(tools.TestBase):
    def write_modules_a_b(self):
        d1 = tools.t_make_temp_directory(self.datadir)
        with open(os.path.join(d1, 'a.py'), 'w') as fh:
            fh.write("set_shell_function('fcn', 'value')")
        with open(os.path.join(d1, 'b.py'), 'w') as fh:
            fh.write("unset_shell_function('fcn')")
        return d1

    @pytest.mark.unit
    def test_set_shell_function(self):
        mc = tools.t_controller(modulepath='')
        mc.set_shell_function('fcn', 'value')
        assert mc.shell_functions['fcn'] == 'value'

    @pytest.mark.unit
    def test_unset_shell_function(self):
        mc = tools.t_controller(modulepath='')
        mc.set_shell_function('fcn', 'value')
        mc.unset_shell_function('fcn')
        assert mc.shell_functions['fcn'] is None

    @pytest.mark.sandbox
    def test_exec_set_shell_function_mode_load(self):
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1)
        mc.load('a')
        assert mc.shell_functions['fcn'] == 'value'

    @pytest.mark.sandbox
    def test_exec_set_shell_function_mode_unload(self):
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1)
        mc.load('a')
        assert mc.shell_functions['fcn'] == 'value'
        mc.unload('a')
        assert mc.shell_functions['fcn'] is None

    @pytest.mark.sandbox
    def test_exec_unset_shell_function_mode_load(self):
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1)
        mc.load('b')
        assert mc.shell_functions['fcn'] is None

    @pytest.mark.sandbox
    def test_exec_unset_shell_function_mode_unload(self):
        # unset_shell_function is a nonop in unload mode
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1)
        mc.load('b')
        assert mc.shell_functions['fcn'] is None
        mc.shell_functions['fcn'] = 'value'
        mc.unload('b')
        assert mc.shell_functions['fcn'] == 'value'

