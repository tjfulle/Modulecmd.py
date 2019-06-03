import pytest

from pymod.main import PymodCommand


def test_command_guide():
    guide = PymodCommand('guide')
    guide('basic_usage')


def test_command_guide_bad():
    guide = PymodCommand('guide')
    try:
        guide('foo')
        assert 0, 'Error should have raised'
    except:
        pass
