import pytest
import pymod.shell


def test_bad_shell():
    with pytest.raises(ValueError):
        shell = pymod.shell.get_shell("fake")


def test_filter_key():
    shell = pymod.shell.get_shell("bash")
    assert not super(pymod.shell.bash.Bash, shell).filter_key("any")
