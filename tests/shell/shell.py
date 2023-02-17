import pytest
import modulecmd.shell


def test_bad_shell():
    with pytest.raises(ValueError):
        shell = modulecmd.shell.get_shell("fake")


def test_filter_key():
    shell = modulecmd.shell.get_shell("bash")
    assert not super(modulecmd.shell.bash.Bash, shell).filter_key("any")
