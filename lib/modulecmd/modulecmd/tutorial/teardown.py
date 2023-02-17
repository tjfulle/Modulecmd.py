import modulecmd.system
import modulecmd.names
import modulecmd.environ

from modulecmd.tutorial.common import rmdir


def teardown():
    env = modulecmd.environ.get(modulecmd.names.tutorial_save_env, serialized=True)
    if env:
        root = modulecmd.environ.get(modulecmd.names.tutorial_root_path)
        modulecmd.system.purge(load_after_purge=False)
        modulecmd.system.restore_clone_impl(env)
        if root:
            rmdir(root)
