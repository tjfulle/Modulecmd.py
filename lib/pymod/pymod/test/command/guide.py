import sys
import pytest
try:
    import docutils
    from docutils import nodes, core
except ImportError:
    docutils = None


pytestmark = pytest.mark.skipif(docutils is None or sys.version_info[:2] == (2,6),
                                reason='Test runs only with python3 with docutils')

from pymod.main import PymodCommand


def test_command_guide_basic():
    guide = PymodCommand('guide')
    guide('basic_usage')


def test_command_guide_bad():
    guide = PymodCommand('guide')
    with pytest.raises(SystemExit):
        guide('foo')
