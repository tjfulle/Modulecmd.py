import os
import pytest

import tools

class TestExecute(tools.TestBase):

    @pytest.mark.mf
    @pytest.mark.unit
    def test_mf_execute(self):
        command = 'touch foobar'
        mc = tools.t_controller(modulepath='')
        fun = mc.wrap_mf_execute('load')
        fun(command, mode='load')
        assert os.path.isfile('foobar')
        os.remove('foobar')
        fun(command, mode='unload')
        assert not os.path.isfile('foobar')

    @pytest.mark.unit
    @pytest.mark.sandbox
    def test_exec_execute(self):
        d1 = tools.t_make_temp_directory(self.datadir)
        f = os.path.join(d1, 'file')
        with open(os.path.join(d1, 'a.py'), 'w') as fh:
            fh.write("execute('touch {0}', mode='load')".format(f))
        mc = tools.t_controller(modulepath=d1)
        mc.load('a')
        assert os.path.isfile(f)
        os.remove(f)
        mc.unload('a')
        assert not os.path.isfile(f)
