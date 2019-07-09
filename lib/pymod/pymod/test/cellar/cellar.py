import random
import string

import pymod.mc
import pymod.names
import pymod.environ
import pymod.modulepath


class dict_with_set(dict):
    def set(self, key, value):
        self[key] = value


def test_cellar_put_acquire():
    # Need to write our own
    env = dict_with_set()
    random_string = lambda: ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(200))
    l_orig = [random_string() for i in range(5)]
    pymod.cellar.put_in_env(env, l_orig)
    l = pymod.cellar.acquire_from_env(env)
    assert l == l_orig


def test_cellar_environ(tmpdir, mock_modulepath):
    assert pymod.mc._mc._loaded_modules is None

    # Need to write our own
    names = 'abc'
    for name in names:
        tmpdir.join(name+'.py').write('')
    mock_modulepath(tmpdir.strpath)

    lm_cellar = []
    for name in names:
        m = pymod.modulepath.get(name)
        ar = pymod.mc.archive_module(m)
        lm_cellar.append(ar)
    pymod.environ.set_lm_cellar(lm_cellar)
    loaded_modules = pymod.mc.get_loaded_modules()
    loaded_module_names = ''.join(m.name for m in loaded_modules)
    assert loaded_module_names == names

