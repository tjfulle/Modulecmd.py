import os
import pytest
import tools
from pymod.defaults import LM_REFCNT_KEY
from pymod.utils import str2dict

class TestPathReferenceCount(tools.TestBase):
    @pytest.mark.unit
    def test_refcount(self):
        f = lambda x: 'f{0}'.format(i)
        d1 = tools.t_make_temp_directory(self.datadir)
        for i in (1, 2, 3):
            filename = os.path.join(d1, f(i) + '.py')
            with open(filename, 'w') as fh:
                fh.write("append_path('path', 'a/f1')")
        mc = tools.t_controller(modulepath=d1, path='/a/path')
        for i in (1, 2, 3):
            mc.load(f(i))
            assert mc['path'] == '/a/path:a/f1'
            assert str2dict(mc[LM_REFCNT_KEY('path')])['a/f1'] == i
        for i in (3, 2, 1):
            mc.unload(f(i))
            if i != 1:
                assert mc['path'] == '/a/path:a/f1'
            else:
                assert mc['path'] == '/a/path'
            if i == 1:
                assert not str2dict(mc[LM_REFCNT_KEY('path')])
            else:
                assert str2dict(mc[LM_REFCNT_KEY('path')])['a/f1'] == i-1

