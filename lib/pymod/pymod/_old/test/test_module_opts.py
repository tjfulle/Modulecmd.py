import os
import pytest

import tools
from pymod.defaults import LM_KEY


class TestModuleOptions(tools.TestBase):

    def write_modules_a_b(self):
        d1 = tools.t_make_temp_directory(self.datadir)
        with open(os.path.join(d1, 'a.py'), 'w') as fh:
            fh.write("whatis('A descriptions')\n")
            fh.write("add_option('+a', action='store_true')\n")
            fh.write("add_option('+b', action='store_false')\n")
            fh.write("add_option('+c', action='store')\n")
            fh.write("add_mutually_exclusive_option('+d', '+e')\n")
            fh.write("opts = parse_opts()\n")
        return d1

    @pytest.mark.sandbox
    def test_exec_load_1(self):
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1)
        mc.load('a')
        opts = mc.environ.get_loaded_modules('opts')
        assert opts.get('a') is None
        assert mc[LM_KEY] == 'a'
        assert mc.modulepath.get_module_by_name('a').is_loaded

    @pytest.mark.sandbox
    def test_exec_load_2(self):
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1)
        mc.moduleopts['a'] = ['+a']
        mc.load('a')
        opts = mc.environ.get_loaded_modules('opts')
        assert opts.get('a') is not None
        assert opts['a'] == ['+a']
        assert mc[LM_KEY] == 'a'
        assert mc.modulepath.get_module_by_name('a').is_loaded

    @pytest.mark.sandbox
    def test_exec_load_3(self):
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1)
        mc.moduleopts['a'] = ['+a', '+b']
        mc.load('a')
        opts = mc.environ.get_loaded_modules('opts')
        assert opts.get('a') is not None
        assert opts['a'] == ['+a', '+b']
        assert mc[LM_KEY] == 'a'
        assert mc.modulepath.get_module_by_name('a').is_loaded

    @pytest.mark.sandbox
    def test_exec_load_4(self):
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1)
        mc.moduleopts['a'] = ['+a', '+b', '+c=baz', '+d']
        mc.load('a')
        opts = mc.environ.get_loaded_modules('opts')
        assert opts.get('a') is not None
        assert opts['a'] == ['+a', '+b', '+c=baz', '+d']
        assert mc[LM_KEY] == 'a'
        assert mc.modulepath.get_module_by_name('a').is_loaded

    @pytest.mark.sandbox
    def test_exec_load_5(self):
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1)
        mc.moduleopts['a'] = ['+d','+e']
        try:
            mc.load('a')
            assert False, 'Parser should have failed with conflicts'
        except:
            pass

