import sys
import pytest

import pymod.shell
from pymod.environ import Environ


@pytest.fixture()
def shell():
    real_shell = pymod.shell._shell
    pymod.shell.set_shell('bash')
    yield
    pymod.shell._shell = real_shell
    pymod.shell.name = real_shell.name


def test_shell_bash_unit(shell):
    assert pymod.shell.name == 'bash'


def test_shell_bash_format_environment_variable(shell):
    s = pymod.shell._shell.format_environment_variable('VAR', 'VAL')
    assert s == 'VAR="VAL";\nexport VAR;'
    s = pymod.shell._shell.format_environment_variable('VAR', None)
    assert s == 'unset VAR;'


def test_shell_bash_format_shell_function(shell):
    s = pymod.shell._shell.format_shell_function('FCN', 'FCN_VAL;')
    assert s == 'FCN() { FCN_VAL; };'
    s = pymod.shell._shell.format_shell_function('FCN', None)
    assert s == 'unset -f FCN 2> /dev/null || true;'


def test_shell_bash_format_alias(shell):
    s = pymod.shell._shell.format_alias('ALIAS', 'ALIAS_VAL')
    assert s == "alias ALIAS='ALIAS_VAL';"
    s = pymod.shell._shell.format_alias('ALIAS', None)
    assert s == 'unalias ALIAS 2> /dev/null || true;'


def test_shell_bash_source_command(shell):
    s = pymod.shell.format_source_command('foo')
    assert s.strip() == 'source foo'


def test_shell_bash_format_output(shell):
    environ = Environ()
    environ.update(
        {'VAR_0': 'VAL_0', 'VAR_None': None})
    environ.aliases.update(
        {'VAR_0': 'VAL_0', 'VAR_None': None})
    environ.shell_functions.update(
        {'VAR_0': 'VAL_0', 'VAR_None': None})
    s = pymod.shell.format_output(environ, aliases=environ.aliases,
                                  shell_functions=environ.shell_functions)
    s = [_ for _ in s.split('\n') if _.split()]
    s_expected = ['VAR_0="VAL_0";',
                  'export VAR_0;',
                  'unset VAR_None;',
                  "alias VAR_0='VAL_0';",
                  'unalias VAR_None 2> /dev/null || true;',
                  'VAR_0() { VAL_0; };',
                  'unset -f VAR_None 2> /dev/null || true;',]
    assert sorted(s) == sorted(s_expected)


def test_shell_bash_filter_env(shell):
    env = {'foo': 'bar', 'BASH_FUNC%%': 'baz'}
    d = pymod.shell.filter_env(env)
    assert d['foo'] == 'bar'
    assert 'BASH_FUNC%%' not in d
