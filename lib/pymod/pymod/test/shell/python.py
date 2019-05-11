import os
import sys

import pymod.shell

class TestPythonShell:
    _shell = None

    @property
    def shell(self):
        if self._shell is None:
            self._shell = pymod.shell._shell('python')
        return self._shell

    def test_shell_csh_format_environment_variable(self):
        s = self.shell.format_environment_variable('VAR', 'VAL')
        assert s == "os.environ['VAR'] = 'VAL'"
        s = self.shell.format_environment_variable('VAR', None)
        assert s == "del os.environ['VAR']"
