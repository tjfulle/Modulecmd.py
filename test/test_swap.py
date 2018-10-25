import os
import pytest

import tools
from pymod.controller import ModuleNotFoundError

class TestSwap(tools.TestBase):
    def write_modules_a_b(self):
        d1 = tools.t_make_temp_directory(self.datadir)
        with open(os.path.join(d1, 'a.py'), 'w') as fh:
            fh.write("setenv('MODULE_SWAP', 'a')")
        with open(os.path.join(d1, 'b.py'), 'w') as fh:
            fh.write("setenv('MODULE_SWAP', 'b')")
        with open(os.path.join(d1, 'c.py'), 'w') as fh:
            fh.write("swap('a', 'b')")
        with open(os.path.join(d1, 'd.py'), 'w') as fh:
            fh.write("swap('a', 'spam')")
        with open(os.path.join(d1, 'e.py'), 'w') as fh:
            fh.write("swap('spam', 'a')")
        with open(os.path.join(d1, 'f.py'), 'w') as fh:
            fh.write("swap('a', 'b')")
        return d1

    @pytest.mark.unit
    def test_swap_1(self):
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1)
        mc.load('a')
        assert mc['MODULE_SWAP'] == 'a'
        mc.swap('a', 'b')
        assert mc['MODULE_SWAP'] == 'b'

    def test_swap_2(self):
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1)
        mc.load('a')
        assert mc['MODULE_SWAP'] == 'a'
        mc.load('c')
        assert mc['MODULE_SWAP'] == 'b'
        # Module b is loaded, nothing to do
        mc.load('c')
        assert mc['MODULE_SWAP'] == 'b'

        # Unload b and then load c.  a is not loaded, but b should still be
        mc.unload('c')
        mc.unload('b')
        mc.load('c')
        assert mc['MODULE_SWAP'] == 'b'

    def test_swap_3(self):
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1)
        mc.load('a')
        try:
            mc.load('d')
            assert False
        except ModuleNotFoundError:
            pass
        try:
            mc.load('e')
            assert False
        except ModuleNotFoundError:
            pass
        mc.load('f')
        assert mc['MODULE_SWAP'] == 'b'

