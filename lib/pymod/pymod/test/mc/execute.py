import os
import pytest
import pymod.mc

@pytest.mark.unit
def test_mc_execute(tmpdir):
    tmpdir.join('foobar').write('')
    f = os.path.join(tmpdir.strpath, 'foobar')
    command = 'touch {0}'.format(f)
    pymod.mc.execute(command)
    assert os.path.isfile(f)

@pytest.mark.unit
def test_mc_execute_2(tmpdir, mock_modulepath):
    """Just load and then unload a"""
    f = os.path.join(tmpdir.strpath, 'foobar')
    tmpdir.join('a.py').write("execute('touch {0}', mode='load')".format(f))
    mp = mock_modulepath(tmpdir.strpath)
    pymod.mc.load('a')
    assert os.path.isfile(f)
    os.remove(f)
    pymod.mc.unload('a')
    assert not os.path.isfile(f)
