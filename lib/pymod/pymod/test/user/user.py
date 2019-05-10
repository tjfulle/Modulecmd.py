import os
import pytest

import pymod.user
import pymod.paths


def test_user_1(tmpdir):
    assert pymod.user.env._module is None
    tmpdir.join('f.py').write('assert 1')
    user_env = pymod.user.UserEnv(os.path.join(tmpdir.strpath, 'f.py'))


def test_user_2(mock_config):
    """Load a and b, b loads c, d, e. Then, unload b (c, d, e should also
    unload)
    """
    d = pymod.paths.user_config_path
    f = os.path.join(d, 'user.py')
    with open(f, 'w') as fh:
        fh.write('foo = 1')
    pymod.user.reset()
    assert pymod.user.env._module is not None
    assert pymod.user.env.foo == 1
    pymod.user.reset()
