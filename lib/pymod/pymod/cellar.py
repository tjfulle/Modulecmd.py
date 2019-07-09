from textwrap import wrap

import pymod.names
import pymod.config
from contrib.util import list_to_str, str_to_list


def acquire_from_env(env):
    """Get the loaded module store"""
    i = 0
    cellar_str = ''
    while True:
        key = '{0}_{1}'.format(pymod.names.loaded_module_cellar, i)
        chunk = env.get(key)
        if chunk is None:
            break
        cellar_str += chunk
        i += 1
    return str_to_list(cellar_str)


def put_in_env(env, cellar):
    """Set the cellar in env"""
    cellar_str = list_to_str(cellar)
    for (i, chunk) in enumerate(wrap(cellar_str, 200)):
        key = '{0}_{1}'.format(pymod.names.loaded_module_cellar, i)
        env.set(key, chunk)
