import os

import pymod.shell
from pymod.environ import Environ


class TestBashShell:
    _shell = None
    @property
    def shell(self):
        if self._shell is None:
            self._shell = pymod.shell._shell('bash')
        return self._shell
    def test_format_environment_variable(self):
        s = self.shell.format_environment_variable('VAR', 'VAL')
        assert s == 'VAR="VAL";\nexport VAR;'
        s = self.shell.format_environment_variable('VAR', None)
        assert s == 'unset VAR;'
    def test_format_shell_function(self):
        s = self.shell.format_shell_function('FCN', 'FCN_VAL;')
        assert s == 'FCN() { FCN_VAL; };'
        s = self.shell.format_shell_function('FCN', None)
        assert s == 'unset -f FCN 2> /dev/null || true;'
    def test_format_alias(self):
        s = self.shell.format_alias('ALIAS', 'ALIAS_VAL')
        assert s == "alias ALIAS='ALIAS_VAL';"
        s = self.shell.format_alias('ALIAS', None)
        assert s == 'unalias ALIAS 2> /dev/null || true;'
    def test_format_output(self):
        environ = Environ()
        environ.update(
            {'VAR_0': 'VAL_0', 'VAR_None': None})
        environ.aliases.update(
            {'VAR_0': 'VAL_0', 'VAR_None': None})
        environ.shell_functions.update(
            {'VAR_0': 'VAL_0', 'VAR_None': None})
        s = self.shell.format_output(environ, environ.aliases, environ.shell_functions)
        s_expected = """VAR_0="VAL_0";\n""" \
                     """export VAR_0;\n""" \
                     """unset VAR_None;\n""" \
                     """alias VAR_0='VAL_0';\n""" \
                     """unalias VAR_None 2> /dev/null || true;\n""" \
                     """VAR_0() { VAL_0; };\n""" \
                     """unset -f VAR_None 2> /dev/null || true;\n"""
        assert s.strip() == s_expected.strip()
