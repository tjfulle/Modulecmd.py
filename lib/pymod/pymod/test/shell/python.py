import os
import sys
import pytest

import pymod.shell


@pytest.fixture()
def shell():
    real_shell = pymod.shell._shell
    pymod.shell.set_shell('python')
    yield
    pymod.shell._shell = real_shell


def test_shell_python_format_environment_variable(shell):
    s = pymod.shell._shell.format_environment_variable('VAR', 'VAL')
    assert s == "os.environ['VAR'] = 'VAL'"
    s = pymod.shell._shell.format_environment_variable('VAR', None)
    assert s == "del os.environ['VAR']"
