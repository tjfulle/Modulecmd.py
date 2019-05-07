import os

import tools
from pymod.shell import get_shell


class TestShell(tools.TestBase):
    @property
    def shell(self, shell=[None]):
        if shell[0] is None:
            shell[0] = get_shell(None)
        return shell[0]
    def test_format_environment_variable(self):
        try:
            self.shell.format_environment_variable('VAR', 'VAL')
            assert False, 'Base method not implemented!'
        except NotImplementedError:
            pass
    def test_format_shell_function(self):
        try:
            self.shell.format_shell_function('VAR', 'VAL')
            assert False, 'Base method not implemented!'
        except NotImplementedError:
            pass
    def test_format_alias(self):
        try:
            self.shell.format_alias('VAR', 'VAL')
            assert False, 'Base method not implemented!'
        except NotImplementedError:
            pass
    def test_dump(self):
        try:
            s = self.shell.dump(['ENV'], {'ENV': 'VAL'})
            assert False, 'Base method not implemented!'
        except NotImplementedError:
            pass
    def test_get_shell(self):
        shell = get_shell('bash')
        assert shell.name == 'bash'
        shell = get_shell('csh')
        assert shell.name == 'csh'
        try:
            shell = get_shell('spam')
            assert False, 'bad shell got through'
        except Exception:
            pass

class TestBashShell(tools.TestBase):
    @property
    def shell(self, shell=[None]):
        if shell[0] is None:
            shell[0] = get_shell('bash')
        return shell[0]
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
    def test_dump(self):
        e_keys = ['VAR_0', 'VAR_None']
        envars = {'VAR_0': 'VAL_0', 'VAR_1': 'VAL_1', 'VAR_None': None}
        a_keys = ['VAR_0', 'VAR_None']
        aliases = {'VAR_0': 'VAL_0', 'VAR_1': 'VAL_1', 'VAR_None': None}
        f_keys = ['VAR_0', 'VAR_None']
        fcns = {'VAR_0': 'VAL_0', 'VAR_1': 'VAL_1', 'VAR_None': None}
        s = self.shell.dump(e_keys, envars, alias_keys=a_keys, aliases=aliases,
                            fcn_keys=f_keys, fcns=fcns)
        s_expected = """VAR_0="VAL_0";\n""" \
                     """export VAR_0;\n""" \
                     """unset VAR_None;\n""" \
                     """alias VAR_0='VAL_0';\n""" \
                     """unalias VAR_None 2> /dev/null || true;\n""" \
                     """VAR_0() { VAL_0; };\n""" \
                     """unset -f VAR_None 2> /dev/null || true;\n"""
        assert s.strip() == s_expected.strip()

class TestCshShell(tools.TestBase):
    @property
    def shell(self, shell=[None]):
        if shell[0] is None:
            shell[0] = get_shell('csh')
        return shell[0]
    def test_format_environment_variable(self):
        s = self.shell.format_environment_variable('VAR', 'VAL')
        assert s == 'setenv VAR "VAL";'
        s = self.shell.format_environment_variable('VAR', None)
        assert s == 'unsetenv VAR;'
    def test_format_shell_function(self):
        s = self.shell.format_shell_function('FCN', 'FCN_VAL;')
        assert s == "alias FCN 'FCN_VAL';"
        s = self.shell.format_shell_function('FCN', None)
        assert s == 'unalias FCN 2> /dev/null || true;'
    def test_format_alias(self):
        s = self.shell.format_alias('ALIAS', 'ALIAS_VAL')
        assert s == "alias ALIAS 'ALIAS_VAL';"
        s = self.shell.format_alias('ALIAS', None)
        assert s == 'unalias ALIAS 2> /dev/null || true;'
        s = self.shell.format_alias('ALIAS', 'ALIAS_VAL $1 $3 $5')
        assert s == "alias ALIAS 'ALIAS_VAL \!:1 \!:3 \!:5';"
        s = self.shell.format_alias('ALIAS', 'ALIAS_VAL $*')
        assert s == "alias ALIAS 'ALIAS_VAL \!*';"
    def test_dump(self):
        e_keys = ['VAR_0', 'VAR_None']
        envars = {'VAR_0': 'VAL_0', 'VAR_1': 'VAL_1', 'VAR_None': None}
        a_keys = ['VAR_0', 'VAR_None']
        aliases = {'VAR_0': 'VAL_0', 'VAR_1': 'VAL_1', 'VAR_None': None}
        f_keys = ['VAR_0', 'VAR_None']
        fcns = {'VAR_0': 'VAL_0', 'VAR_1': 'VAL_1', 'VAR_None': None}
        s = self.shell.dump(e_keys, envars, alias_keys=a_keys, aliases=aliases,
                            fcn_keys=f_keys, fcns=fcns)
        s_expected = """setenv VAR_0 "VAL_0";\n""" \
                     """unsetenv VAR_None;\n""" \
                     """alias VAR_0 'VAL_0';\n""" \
                     """unalias VAR_None 2> /dev/null || true;\n""" \
                     """alias VAR_0 'VAL_0';\n""" \
                     """unalias VAR_None 2> /dev/null || true;\n"""
        assert s.strip() == s_expected.strip()
