import os
import sys
import pytest
import string

import modulecmd.shell
from modulecmd.environ import Environ


@pytest.fixture()
def shell():
    real_shell = modulecmd.shell._shell
    modulecmd.shell.set_shell("csh")
    yield
    modulecmd.shell._shell = real_shell
    modulecmd.shell.name = real_shell.name


def test_shell_csh_unit(shell):
    assert modulecmd.shell.name == "csh"


def test_shell_csh_format_environment_variable(shell):
    s = modulecmd.shell._shell.format_environment_variable("VAR", "VAL")
    assert s == 'setenv VAR "VAL";'
    s = modulecmd.shell._shell.format_environment_variable("VAR", None)
    assert s == "unsetenv VAR;"


def test_shell_csh_format_shell_function(shell):
    s = modulecmd.shell._shell.format_shell_function("FCN", "FCN_VAL;")
    assert s == "alias FCN 'FCN_VAL';"
    s = modulecmd.shell._shell.format_shell_function("FCN", None)
    assert s == "unalias FCN 2> /dev/null || true;"


def test_shell_csh_format_alias(shell):
    s = modulecmd.shell._shell.format_alias("ALIAS", "ALIAS_VAL")
    assert s == "alias ALIAS 'ALIAS_VAL';"
    s = modulecmd.shell._shell.format_alias("ALIAS", None)
    assert s == "unalias ALIAS 2> /dev/null || true;"
    s = modulecmd.shell._shell.format_alias("ALIAS", "ALIAS_VAL $1 $3 $5")
    assert s == "alias ALIAS 'ALIAS_VAL \!:1 \!:3 \!:5';"
    s = modulecmd.shell._shell.format_alias("ALIAS", "ALIAS_VAL $*")
    assert s == "alias ALIAS 'ALIAS_VAL \!*';"


def test_shell_csh_source_command(shell):
    s = modulecmd.shell.format_source_command("foo")
    assert s.strip() == "source foo"


def test_shell_csh_format_output(shell):
    environ = Environ()
    environ.update({"VAR_0": "VAL_0", "VAR_None": None})
    environ.aliases.update({"VAR_0": "VAL_0", "VAR_None": None})
    environ.shell_functions.update({"VAR_0": "VAL_0", "VAR_None": None})
    s = modulecmd.shell.format_output(environ, environ.aliases, environ.shell_functions)
    s = [_ for _ in s.split("\n") if _.split()]
    s_expected = [
        'setenv VAR_0 "VAL_0";',
        "unsetenv VAR_None;",
        "alias VAR_0 'VAL_0';",
        "unalias VAR_None 2> /dev/null || true;",
        "alias VAR_0 'VAL_0';",
        "unalias VAR_None 2> /dev/null || true;",
    ]
    assert sorted(s) == sorted(s_expected)


def test_shell_csh_var_overlimit(shell):
    environ = Environ()
    limit = modulecmd.shell.csh.CSH_LIMIT
    toolong = "A" * (limit + 5)
    environ.update({"VAR": toolong})
    s = modulecmd.shell.format_output(environ, environ.aliases, environ.shell_functions)
    s_expected = 'setenv VAR "{0}";'.format("A" * limit)
    assert s.strip() == s_expected


def test_shell_csh_path_overlimit(shell):
    environ = Environ()
    limit = modulecmd.shell.csh.CSH_LIMIT
    letters = string.ascii_uppercase
    n = int(float(limit) / len(letters)) + 10
    path = []
    for i in range(len(letters)):
        path.append(letters[i] * n)
    spath = os.pathsep.join(path)
    environ.update({"PATH": spath})
    s = modulecmd.shell.format_output(environ, {}, {}).strip()
    end = '/usr/bin{0}/bin";'.format(os.pathsep)
    p = os.pathsep.join(path[:-2]) + os.pathsep + end
    s_expected = 'setenv PATH "{0}'.format(p)
    assert s.endswith(end)
    assert s == s_expected
