import os

import modulecmd.system
import modulecmd.user
import modulecmd.paths


def test_user_1(tmpdir):
    assert modulecmd.user.env._module is None
    tmpdir.join("f.py").write("assert 1")
    user_env = modulecmd.user.UserEnv(os.path.join(tmpdir.strpath, "f.py"))


def test_user_2(mock_config):
    d = modulecmd.paths.user_config_path
    f = os.path.join(d, "user.py")
    with open(f, "w") as fh:
        fh.write("foo = 1")
    modulecmd.user.reset()
    assert modulecmd.user.env._module is not None
    assert modulecmd.user.env.foo == 1
    os.remove(f)
    modulecmd.user.reset()


def test_user_3(tmpdir, mock_config, mock_modulepath):
    d = modulecmd.paths.user_config_path
    f = os.path.join(d, "user.py")

    with open(f, "w") as fh:
        fh.write("foo = 1")
    modulecmd.user.reset()

    one = tmpdir.mkdir("1")
    one.join("a.py").write("assert user_env.foo == 1\n")

    mock_modulepath(one.strpath)
    a = modulecmd.system.load("a")
    assert a.is_loaded

    os.remove(f)
    modulecmd.user.reset()


def test_user_4(tmpdir, mock_modulepath):
    one = tmpdir.mkdir("1")
    one.join("a.py").write("x = user_env.x\nassert x == 10")
    tmpdir.join("user.py").write("x = 10")
    f = tmpdir.join("user.py").strpath
    user_env = modulecmd.user.UserEnv(f)
    modulecmd.user.set_user_env(user_env)
    mock_modulepath(one.strpath)
    a = modulecmd.system.load("a")
    os.remove(f)
    modulecmd.user.reset()
