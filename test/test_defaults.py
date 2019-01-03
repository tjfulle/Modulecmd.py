import os
import sys
import pytest

import tools
import pymod.defaults as defaults

class TestDefaults(tools.TestBase):

    def test_LM_REFCNT_KEY(self):
        x = defaults.LM_REFCNT_KEY()
        x = defaults.LM_REFCNT_KEY(name='FOO')
