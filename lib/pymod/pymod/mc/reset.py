import pymod.mc
import pymod.environ


def reset():
    initial_env = pymod.environ.get(pymod.names.initial_env, serialized=True)
    pymod.mc.clone.restore_impl(initial_env)
    return initial_env
