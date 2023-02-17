import modulecmd.system
import modulecmd.environ
import modulecmd.names


def test_mc_reset(tmpdir, mock_modulepath):
    initial_env = modulecmd.environ.copy(include_os=True)
    assert modulecmd.names.modulepath in initial_env
    modulecmd.environ.set(modulecmd.names.initial_env, initial_env, serialize=True)
    env = modulecmd.system.reset()
    # MODULEPATH is Popped
    assert not modulecmd.names.modulepath in env
    mp = initial_env.pop(modulecmd.names.modulepath)
    assert mp == modulecmd.modulepath._path.value
    for key, val in initial_env.items():
        assert key in env
        reset_val = env.pop(key)
        assert reset_val == val
    assert len(env.keys()) == 0
