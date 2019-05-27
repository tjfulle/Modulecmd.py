import sys
import pytest

import pymod.shell
from pymod.environ import Environ


@pytest.fixture()
def shell():
    real_shell = pymod.shell._shell
    pymod.shell.set_shell('csh')
    yield
    pymod.shell._shell = real_shell
    pymod.shell.name = real_shell.name


def test_shell_csh_unit(shell):
    assert pymod.shell.name == 'csh'


def test_shell_csh_format_environment_variable(shell):
    s = pymod.shell._shell.format_environment_variable('VAR', 'VAL')
    assert s == 'setenv VAR "VAL";'
    s = pymod.shell._shell.format_environment_variable('VAR', None)
    assert s == 'unsetenv VAR;'


def test_shell_csh_format_shell_function(shell):
    s = pymod.shell._shell.format_shell_function('FCN', 'FCN_VAL;')
    assert s == "alias FCN 'FCN_VAL';"
    s = pymod.shell._shell.format_shell_function('FCN', None)
    assert s == 'unalias FCN 2> /dev/null || true;'


def test_shell_csh_format_alias(shell):
    s = pymod.shell._shell.format_alias('ALIAS', 'ALIAS_VAL')
    assert s == "alias ALIAS 'ALIAS_VAL';"
    s = pymod.shell._shell.format_alias('ALIAS', None)
    assert s == 'unalias ALIAS 2> /dev/null || true;'
    s = pymod.shell._shell.format_alias('ALIAS', 'ALIAS_VAL $1 $3 $5')
    assert s == "alias ALIAS 'ALIAS_VAL \!:1 \!:3 \!:5';"
    s = pymod.shell._shell.format_alias('ALIAS', 'ALIAS_VAL $*')
    assert s == "alias ALIAS 'ALIAS_VAL \!*';"


def test_shell_csh_source_command(shell):
    s = pymod.shell.format_source_command('foo')
    assert s.strip() == 'source foo'


def test_shell_csh_format_output(shell):
    environ = Environ()
    environ.update(
        {'VAR_0': 'VAL_0', 'VAR_None': None})
    environ.aliases.update(
        {'VAR_0': 'VAL_0', 'VAR_None': None})
    environ.shell_functions.update(
        {'VAR_0': 'VAL_0', 'VAR_None': None})
    s = pymod.shell.format_output(environ, environ.aliases, environ.shell_functions)
    s = [_ for _ in s.split('\n') if _.split()]
    s_expected = ['setenv VAR_0 "VAL_0";',
                  'unsetenv VAR_None;',
                  "alias VAR_0 'VAL_0';",
                  'unalias VAR_None 2> /dev/null || true;',
                  "alias VAR_0 'VAL_0';",
                  'unalias VAR_None 2> /dev/null || true;',]
    assert sorted(s) == sorted(s_expected)
