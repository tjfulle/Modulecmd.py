import pymod.mc
import pymod.environ


def init(dirnames):
    initial_env = pymod.environ.copy(include_os=True)
    for dirname in dirnames:
        pymod.mc.use(dirname, append=True)
    if pymod.collection.is_collection(pymod.names.default_user_collection): # pragma: no cover
        pymod.mc.restore(pymod.names.default_user_collection)
    pymod.environ.set_dict(pymod.names.initial_env, initial_env)
    return
