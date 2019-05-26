import pymod.mc
import pymod.environ


def reset():
    initial_env = pymod.environ.get_dict(pymod.names.initial_env)
    pymod.mc.restore_clone_impl(initial_env)
    return initial_env