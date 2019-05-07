import os
import pytest

import tools
from pymod.controller import ModuleNotFoundError


class TestReload(tools.TestBase):
    def write_modules(self):
        d1 = tools.t_make_temp_directory(self.datadir)
        with open(os.path.join(d1, 'a.py'), 'w') as fh:
            fh.write("append_path('path', 'a')\n")
        with open(os.path.join(d1, 'b.py'), 'w') as fh:
            fh.write("append_path('path', 'b')\n")
        with open(os.path.join(d1, 'c.py'), 'w') as fh:
            fh.write("add_option('+x')\n")
            fh.write("append_path('path', 'c')\n")
        return d1

    @pytest.mark.sandbox
    def test_exec_reload_1(self):
        d1 = self.write_modules()
        mc = tools.t_controller(modulepath=d1)
        mc.load('a')
        mc.load('b')
        mc.load('c', options=['+x'])
        assert mc.modulepath.get_module_by_name('a').is_loaded
        assert mc.modulepath.get_module_by_name('b').is_loaded
        assert mc.modulepath.get_module_by_name('c').is_loaded
        assert mc['path'] == 'a:b:c'
        mc.reload('a')
        assert mc.modulepath.get_module_by_name('a').is_loaded
        assert mc.modulepath.get_module_by_name('b').is_loaded
        assert mc.modulepath.get_module_by_name('c').is_loaded
        assert mc['path'] == 'a:b:c'
        mc.reload('b')
        assert mc.modulepath.get_module_by_name('a').is_loaded
        assert mc.modulepath.get_module_by_name('b').is_loaded
        assert mc.modulepath.get_module_by_name('c').is_loaded
        assert mc['path'] == 'a:b:c'
        mc.reload('c')
        assert mc.modulepath.get_module_by_name('a').is_loaded
        assert mc.modulepath.get_module_by_name('b').is_loaded
        assert mc.modulepath.get_module_by_name('c').is_loaded
        assert mc['path'] == 'a:b:c'
        try:
            mc.reload('xyz')
            assert False
        except ModuleNotFoundError:
            pass

