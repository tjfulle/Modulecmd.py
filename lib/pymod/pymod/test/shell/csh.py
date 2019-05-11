import os
import sys
import pytest

import pymod.shell
from pymod.environ import Environ

class TestCshShell:
    _shell = None

    @property
    def shell(self):
        if self._shell is None:
            self._shell = pymod.shell._shell('csh')
        return self._shell

    def test_shell_csh_format_environment_variable(self):
        s = self.shell.format_environment_variable('VAR', 'VAL')
        assert s == 'setenv VAR "VAL";'
        s = self.shell.format_environment_variable('VAR', None)
        assert s == 'unsetenv VAR;'

    def test_shell_csh_format_shell_function(self):
        s = self.shell.format_shell_function('FCN', 'FCN_VAL;')
        assert s == "alias FCN 'FCN_VAL';"
        s = self.shell.format_shell_function('FCN', None)
        assert s == 'unalias FCN 2> /dev/null || true;'

    def test_shell_csh_format_alias(self):
        s = self.shell.format_alias('ALIAS', 'ALIAS_VAL')
        assert s == "alias ALIAS 'ALIAS_VAL';"
        s = self.shell.format_alias('ALIAS', None)
        assert s == 'unalias ALIAS 2> /dev/null || true;'
        s = self.shell.format_alias('ALIAS', 'ALIAS_VAL $1 $3 $5')
        assert s == "alias ALIAS 'ALIAS_VAL \!:1 \!:3 \!:5';"
        s = self.shell.format_alias('ALIAS', 'ALIAS_VAL $*')
        assert s == "alias ALIAS 'ALIAS_VAL \!*';"

    def test_shell_csh_source_command(self):
        s = self.shell.format_source_command('foo')
        assert s.strip() == 'source foo'

    @pytest.mark.skipif(sys.version_info[0]==2, reason='dicts not ordered in 2.7')
    def test_shell_csh_format_output(self):
        environ = Environ()
        environ.update(
            {'VAR_0': 'VAL_0', 'VAR_None': None})
        environ.aliases.update(
            {'VAR_0': 'VAL_0', 'VAR_None': None})
        environ.shell_functions.update(
            {'VAR_0': 'VAL_0', 'VAR_None': None})
        s = self.shell.format_output(environ, environ.aliases, environ.shell_functions)
        s_expected = """setenv VAR_0 "VAL_0";\n""" \
                     """unsetenv VAR_None;\n""" \
                     """alias VAR_0 'VAL_0';\n""" \
                     """unalias VAR_None 2> /dev/null || true;\n""" \
                     """alias VAR_0 'VAL_0';\n""" \
                     """unalias VAR_None 2> /dev/null || true;\n"""
        assert s.strip() == s_expected.strip()
