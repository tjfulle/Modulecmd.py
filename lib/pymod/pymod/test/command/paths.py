import pytest

from pymod.main import PymodCommand


def test_command_paths():
    PymodCommand('paths')()
