import sys
import pytest

import modulecmd.shell
from modulecmd.environ import Environ


@pytest.fixture()
def shell():
    real_shell = modulecmd.shell._shell
    modulecmd.shell.set_shell("bash")
    yield
    modulecmd.shell._shell = real_shell
    modulecmd.shell.name = real_shell.name


def test_shell_bash_unit(shell):
    assert modulecmd.shell.name == "bash"


def test_shell_bash_format_environment_variable(shell):
    s = modulecmd.shell._shell.format_environment_variable("VAR", "VAL")
    assert s == 'VAR="VAL";\nexport VAR;'
    s = modulecmd.shell._shell.format_environment_variable("VAR", None)
    assert s == "unset VAR;"


def test_shell_bash_format_shell_function(shell):
    s = modulecmd.shell._shell.format_shell_function("FCN", "FCN_VAL;")
    assert s == "FCN() { FCN_VAL; };"
    s = modulecmd.shell._shell.format_shell_function("FCN", None)
    assert s == "unset -f FCN 2> /dev/null || true;"


def test_shell_bash_format_alias(shell):
    s = modulecmd.shell._shell.format_alias("ALIAS", "ALIAS_VAL")
    assert s == "alias ALIAS='ALIAS_VAL';"
    s = modulecmd.shell._shell.format_alias("ALIAS", None)
    assert s == "unalias ALIAS 2> /dev/null || true;"


def test_shell_bash_source_command(shell):
    s = modulecmd.shell.format_source_command("foo")
    assert s.strip() == "source foo"


def test_shell_bash_format_output(shell):
    environ = Environ()
    environ.update({"VAR_0": "VAL_0", "VAR_None": None})
    environ.aliases.update({"VAR_0": "VAL_0", "VAR_None": None})
    environ.shell_functions.update({"VAR_0": "VAL_0", "VAR_None": None})
    s = modulecmd.shell.format_output(
        environ, aliases=environ.aliases, shell_functions=environ.shell_functions
    )
    s = [_ for _ in s.split("\n") if _.split()]
    s_expected = [
        'VAR_0="VAL_0";',
        "export VAR_0;",
        "unset VAR_None;",
        "alias VAR_0='VAL_0';",
        "unalias VAR_None 2> /dev/null || true;",
        "VAR_0() { VAL_0; };",
        "unset -f VAR_None 2> /dev/null || true;",
    ]
    assert sorted(s) == sorted(s_expected)


def test_shell_bash_filter_env(shell):
    env = {"foo": "bar", "BASH_FUNC%%": "baz"}
    d = modulecmd.shell.filter_env(env)
    assert d["foo"] == "bar"
    assert "BASH_FUNC%%" not in d
