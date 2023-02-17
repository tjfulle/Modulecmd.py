import pytest

from modulecmd.main import PymodCommand


def test_command_paths():
    PymodCommand("paths")()
