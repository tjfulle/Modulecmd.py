import pymod.mc
import pymod.environ
import pymod.names


def test_mc_reset(tmpdir, mock_modulepath):
    initial_env = pymod.mc.cloned_env()
    pymod.environ.set_dict(pymod.names.initial_env, initial_env)
    env = pymod.mc.reset()
    for key, val in initial_env.items():
        if key != pymod.names.modulepath:
            assert key in env
        reset_val = env.pop(key, None)
        if reset_val:
            assert reset_val == val
    assert len(env.keys()) == 0