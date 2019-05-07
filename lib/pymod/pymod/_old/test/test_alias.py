import os
import pytest

import tools

class TestAlias(tools.TestBase):
    def write_modules_a_b(self):
        d1 = tools.t_make_temp_directory(self.datadir)
        with open(os.path.join(d1, 'a.py'), 'w') as fh:
            fh.write("set_alias('alias', 'value')")
        with open(os.path.join(d1, 'b.py'), 'w') as fh:
            fh.write("unset_alias('alias')")
        return d1

    @pytest.mark.unit
    def test_set_alias(self):
        mc = tools.t_controller(modulepath='')
        mc.set_alias('alias', 'value')
        assert mc.aliases['alias'] == 'value'

    @pytest.mark.unit
    def test_unset_alias(self):
        mc = tools.t_controller(modulepath='')
        mc.set_alias('alias', 'value')
        mc.unset_alias('alias')
        assert mc.aliases['alias'] is None

    @pytest.mark.sandbox
    def test_exec_set_alias_mode_load(self):
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1)
        mc.load('a')
        assert mc.aliases['alias'] == 'value'

    @pytest.mark.sandbox
    def test_exec_set_alias_mode_unload(self):
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1)
        mc.load('a')
        assert mc.aliases['alias'] == 'value'
        mc.unload('a')
        assert mc.aliases['alias'] is None

    @pytest.mark.sandbox
    def test_exec_unset_alias_mode_load(self):
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1)
        mc.load('b')
        assert mc.aliases['alias'] is None

    @pytest.mark.sandbox
    def test_exec_unset_alias_mode_unload(self):
        # unset_alias is a nonop in unload mode
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1)
        mc.load('b')
        assert mc.aliases['alias'] is None
        mc.aliases['alias'] = 'value'
        mc.unload('b')
        assert mc.aliases['alias'] == 'value'

