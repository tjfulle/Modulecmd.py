import pymod.mc
import pymod.environ
import pymod.names


def test_mc_reset(tmpdir, mock_modulepath):
    initial_env = pymod.environ.copy(include_os=True)
    assert pymod.names.modulepath in initial_env
    pymod.environ.set(pymod.names.initial_env, initial_env, serialize=True)
    env = pymod.mc.reset()
    # MODULEPATH is Popped
    assert not pymod.names.modulepath in env
    mp = initial_env.pop(pymod.names.modulepath)
    assert mp == pymod.modulepath._path.value
    for key, val in initial_env.items():
        assert key in env
        reset_val = env.pop(key)
        assert reset_val == val
    assert len(env.keys()) == 0
