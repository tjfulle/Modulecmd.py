import os
import sys
import pytest

import tools
from pymod.utils import *
import pymod.defaults as defaults

class TestDefaults(tools.TestBase):

    def test_collections_filename(self):
        default = defaults.collections_filename()
        assert default == os.path.join(self.dotdir, 'collections.json')

    def test_clones_filename(self):
        default = defaults.clones_filename()
        assert default == os.path.join(self.dotdir, 'clones.json')

    def test_LM_REFCNT_KEY(self):
        x = defaults.LM_REFCNT_KEY()
        x = defaults.LM_REFCNT_KEY(name='FOO')
