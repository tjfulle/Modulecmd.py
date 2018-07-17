import os
import pytest

import tools
from pymod.controller import ModuleNotFoundError

class TestDefaultModule(tools.TestBase):

    @pytest.mark.unit
    @pytest.mark.modulepath
    def test_default_module(self):
        d1 = tools.t_make_temp_directory(self.datadir)
        d2 = tools.t_make_temp_directory(self.datadir)
        tools.t_touch(os.path.join(d1, 'a/1.0.py'))
        tools.t_touch(os.path.join(d1, 'a/2.0.py'))
        tools.t_touch(os.path.join(d2, 'a/3.0.py'))
        mc = tools.t_controller(modulepath=':'.join((d1,d2)))
        # Load it.  Should get module with highest version
        m = mc.load('a')
        assert m.version == '3.0'
        mc.edit('a')
        try:
            mc.edit('foo')
            assert False, 'should have failed edit'
        except ModuleNotFoundError:
            pass

