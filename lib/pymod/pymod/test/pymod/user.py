import os
import pytest

import pymod.user
import pymod.paths


def test_user_1(tmpdir):
    assert pymod.user.env._module is None
    tmpdir.join('f.py').write('assert 1')
    user_env = pymod.user.UserEnv(os.path.join(tmpdir.strpath, 'f.py'))


def test_user_2(mock_config):
    d = pymod.paths.user_config_path
    f = os.path.join(d, 'user.py')
    with open(f, 'w') as fh:
        fh.write('foo = 1')
    pymod.user.reset()
    assert pymod.user.env._module is not None
    assert pymod.user.env.foo == 1
    os.remove(f)
    pymod.user.reset()


def test_user_3(tmpdir, mock_config, mock_modulepath):
    d = pymod.paths.user_config_path
    f = os.path.join(d, 'user.py')

    with open(f, 'w') as fh:
        fh.write('foo = 1')
    pymod.user.reset()

    one = tmpdir.mkdir('1')
    one.join('a.py').write('assert user_env.foo == 1\n')

    mp = mock_modulepath(one.strpath)
    a = pymod.mc.load('a')
    assert a.is_loaded

    os.remove(f)
    pymod.user.reset()
