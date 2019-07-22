import pytest
try:
    import docutils
    from docutils import nodes, core
except ImportError:
    docutils = None

from pymod.main import PymodCommand


@pytest.mark.skipif(docutils is None, reason='Test requires docutils')
def test_command_guide_basic():
    guide = PymodCommand('guide')
    guide('basic_usage')


@pytest.mark.skipif(docutils is None, reason='Test requires docutils')
def test_command_guide_bad():
    guide = PymodCommand('guide')
    try:
        guide('foo')
        assert 0, 'Error should have raised'
    except:
        pass
