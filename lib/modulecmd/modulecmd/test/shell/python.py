import pytest

import modulecmd.shell


@pytest.fixture()
def shell():
    real_shell = modulecmd.shell._shell
    modulecmd.shell.set_shell("python")
    yield
    modulecmd.shell._shell = real_shell


def test_shell_python_format_environment_variable(shell):
    s = modulecmd.shell._shell.format_environment_variable("VAR", "VAL")
    assert s == "os.environ['VAR'] = 'VAL'"
    s = modulecmd.shell._shell.format_environment_variable("VAR", None)
    assert s == "del os.environ['VAR']"
