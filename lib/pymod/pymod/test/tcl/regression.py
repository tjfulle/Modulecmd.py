import pytest

import pymod.names
import pymod.modes
import pymod.config
import pymod.module
import pymod.modulepath
from pymod.module.tcl2py import tcl2py

pytestmark = pytest.mark.skipif(not pymod.config.has_tclsh,
                                reason='No tclsh')


@pytest.mark.tcl
def test_tcl_env(tmpdir, mock_modulepath):
    f = tmpdir.join('f').write('''\
#%Module1.0
if [info exists env(FOO)] {
  setenv BAZ $env(FOO)
} else {
  setenv BAZ SPAM
}
''')
    mock_modulepath(tmpdir.strpath)
    pymod.environ.set('FOO', 'BAR')
    m = pymod.mc.load('f')
    assert pymod.environ.get('BAZ') == 'BAR'
    assert m.is_loaded
    pymod.mc.unload('f')

    pymod.environ.environ.pop('FOO')
    m = pymod.mc.load('f')
    assert pymod.environ.get('BAZ') == 'SPAM'
    pymod.environ.environ.pop('BAZ')
    pymod.environ.environ.pop('FOO', None)


@pytest.mark.tcl
def test_tcl_env_break(tmpdir, mock_modulepath):
    f = tmpdir.join('f').write('''\
#%Module1.0
if { [info exists env(FOO)] } {
  break
} else {
  setenv BAZ SPAM
}
''')
    mock_modulepath(tmpdir.strpath)

    pymod.environ.environ.pop('FOO', None)
    m = pymod.mc.load('f')
    assert pymod.environ.get('BAZ') == 'SPAM'
    assert m.is_loaded
    pymod.mc.unload('f')

    pymod.environ.set('FOO', 'BAR')
    pymod.environ.environ.pop('BAZ', None)
    m = pymod.mc.load('f')
    assert pymod.environ.get('BAZ') is None
    assert not m.is_loaded

    pymod.environ.environ.pop('FOO')
