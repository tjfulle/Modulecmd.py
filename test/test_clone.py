import os
import pytest

import tools
from pymod.cfg import cfg

class TestClone(tools.TestBase):
    def test_write_read_clones(self):
        d1 = tools.t_make_temp_directory(self.datadir)
        with open(os.path.join(d1, 'a.py'), 'w') as fh:
            fh.write('append_path("path", "/a/path")')
        d2 = tools.t_make_temp_directory(self.datadir)
        with open(os.path.join(d2, 'b.py'), 'w') as fh:
            fh.write('append_path("path", "/b/path")')
        mc = tools.t_controller(modulepath=':'.join((d1, d2)))
        mc.load('a')
        mc.load('b')

        env1 = mc.environ.copy()
        mc.clone_current_environment('myclone')
        assert os.path.isfile(cfg.clones_filename)
        mc.unload('a')
        mc.unload('b')
        mc.restore_clone('myclone')
        env2 = mc.environ.copy()
        assert env1 == env2

        mc.remove_clone('myclone')
        mc.display_clones()
        mc.display_clones(terse=True)
