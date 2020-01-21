import pymod.mc
import pymod.names
import pymod.environ

from pymod.tutorial.common import rmdir


def teardown():
    env = pymod.environ.get_deserialized(pymod.names.tutorial_save_env)
    if env:
        root = pymod.environ.get(pymod.names.tutorial_root_path)
        pymod.mc.purge(load_after_purge=False)
        pymod.mc.clone.restore_impl(env)
        if root:
            rmdir(root)
