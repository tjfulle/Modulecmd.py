import os
import pytest

import tools
from pymod.defaults import LM_KEY, LM_FILES_KEY


class TestPurge(tools.TestBase):

    def write_modules_a_b(self):
        d1 = tools.t_make_temp_directory(self.datadir)
        with open(os.path.join(d1, 'a.py'), 'w') as fh:
            fh.write('setenv("envar1", "val1")\n'
                     'setenv("envar2", "val2")\n'
                     'append_path("path", "/c/path", "/d/path")\n'
                     'remove_path("key", "/d/path")')
        with open(os.path.join(d1, 'b.py'), 'w') as fh:
            fh.write("load('a')")
        return d1

    @pytest.mark.sandbox
    def test_purge(self):
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1,
                          path='/a/path:/b/path',
                          key='/c/path:/d/path')
        mc.load('b')
        assert mc['envar1'] == 'val1'
        assert mc['envar2'] == 'val2'
        assert mc.environ[LM_KEY] == 'a:b'
        lm_files = ':'.join([os.path.join(d1, 'a.py'), os.path.join(d1, 'b.py')])
        assert mc.environ[LM_FILES_KEY] == lm_files
        mc.purge()
        assert not mc[LM_KEY]
        assert not mc[LM_FILES_KEY]
        assert mc['path'] == '/a/path:/b/path'
        assert mc['key'] == '/c/path'
        assert mc['envar1'] is None
        assert mc['envar2'] is None

