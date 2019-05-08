import pytest

import pymod.mc
import pymod.modulepath


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds

    one = tmpdir.mkdir('1')
    a = one.mkdir('a')
    a.join('1.0.py').write(m.setenv('a', '1.0'))
    a.join('1.5.py').write(m.setenv('a', '1.5'))

    two = tmpdir.mkdir('2')
    a = two.mkdir('a')
    a.join('1.0.py').write(m.setenv('a', '1.0'))
    a.join('2.0.py').write(m.setenv('a', '2.0'))

    three = tmpdir.mkdir('3')
    a = three.mkdir('a')
    a.join('1.0.py').write(m.setenv('a', '1.0'))
    a.join('3.0.py').write(m.setenv('a', '3.0'))

    four = tmpdir.mkdir('4')
    a = four.mkdir('a')
    a.join('1.0.py').write(m.setenv('a', '1.0'))
    a.join('4.0.py').write(m.setenv('a', '4.0'))

    ns = namespace()
    ns.one = one.strpath
    ns.two = two.strpath
    ns.three = three.strpath
    ns.four = four.strpath
    return ns


@pytest.mark.unit
def test_unuse(modules_path, mock_modulepath):
    """Just load and then unload a"""
    is_module = lambda x: pymod.modulepath.get(x) is not None
    mp = mock_modulepath(
        [modules_path.one, modules_path.two, modules_path.three, modules_path.four])

    a = pymod.modulepath.get('a')
    assert a.version.string == '4.0'
    assert is_module('a/1.0')
    assert is_module('a/1.5')
    assert is_module('a/2.0')
    assert is_module('a/3.0')
    assert is_module('a/4.0')

    pymod.mc.unuse(modules_path.four)
    a = pymod.modulepath.get('a')
    assert a.version.string == '3.0'
    assert is_module('a/1.0')
    assert is_module('a/1.5')
    assert is_module('a/2.0')
    assert is_module('a/3.0')
    assert not is_module('a/4.0')

    pymod.mc.unuse(modules_path.three)
    a = pymod.modulepath.get('a')
    assert a.version.string == '2.0'
    assert is_module('a/1.0')
    assert is_module('a/1.5')
    assert is_module('a/2.0')
    assert not is_module('a/3.0')
    assert not is_module('a/4.0')

    pymod.mc.unuse(modules_path.two)
    a = pymod.modulepath.get('a')
    assert a.version.string == '1.5'
    assert is_module('a/1.0')
    assert is_module('a/1.5')
    assert not is_module('a/2.0')
    assert not is_module('a/3.0')
    assert not is_module('a/4.0')

    pymod.mc.unuse(modules_path.one)
    a = pymod.modulepath.get('a')
    assert a is None
    assert not is_module('a/1.0')
    assert not is_module('a/1.5')
    assert not is_module('a/2.0')
    assert not is_module('a/3.0')
    assert not is_module('a/4.0')
