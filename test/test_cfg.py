import os
import sys
import pytest

import tools
from pymod.utils import *
from pymod.cfg import cfg

class TestDefaults(tools.TestBase):

    def test_cfg(self):
        f = cfg.collections_filename
        assert f == os.path.join(cfg.dot_dir, 'collections.json')

        f = cfg.clones_filename
        assert f == os.path.join(cfg.dot_dir, 'clones.json')

        f = cfg.user_env_filename
        assert f == os.path.join(cfg.dot_dir, 'user.py')

        assert cfg.dot_dir == self.dotdir
        assert cfg.debug == False
        assert cfg.verbosity in (1, 2)
        assert cfg.warn_all == True
        assert cfg.cache_avail == True
        assert cfg.stop_on_error == True
        assert cfg.resolve_conflicts == False
        assert cfg.editor == 'vim'
