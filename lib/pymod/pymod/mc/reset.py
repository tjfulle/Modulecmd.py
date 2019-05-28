import pymod.mc
import pymod.environ


def reset():
    initial_env = pymod.environ.get_dict(pymod.names.initial_env)
    pymod.mc.clone.restore_impl(initial_env)
    return initial_env
