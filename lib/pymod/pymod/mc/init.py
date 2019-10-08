import pymod.mc
import pymod.environ


def init(dirnames):
    initial_env = pymod.environ.copy(include_os=True)
    if pymod.collection.contains(pymod.names.default_user_collection): # pragma: no cover
        pymod.mc.collection.restore(pymod.names.default_user_collection)
    for dirname in dirnames:
        pymod.mc.use(dirname, append=True)
    pymod.environ.set_serialized(pymod.names.initial_env, initial_env)
    return
