import os
import pytest

import pymod.mc
import pymod.error
import pymod.environ

"""Test of module hierarchy.

core/
  ucc/1.0.py
  ucc/2.0.py
compiler/
  ucc/
    1.0/
      a/
        1.0.py
      umpi/
        1.0.py
        2.0.py
    2.0/
      a/
        1.0.py
      umpi/
        1.0.py
        2.0.py
mpi/
    ucc/
      1.0/
        umpi/
          1.0/
            b/
              1.0.py
              2.0.py

"""


@pytest.fixture()
def modules_path(tmpdir, namespace, modulecmds):
    m = modulecmds
    cc = 'ucc'
    mpi = 'umpi'
    versions = ('1.0', '2.0')

    core = tmpdir.mkdir('core')
    compiler = tmpdir.mkdir('compiler')

    # Build the compiler directory tree
    ucc = compiler.mkdir('ucc')
    for v in versions:
        uccv = ucc.mkdir(v)
        a = uccv.mkdir('a')
        a.join('1.0.py').write(m.setenv('a', '1.0'))

    # Build the core modules
    ucc = core.mkdir('ucc')
    for v in versions:
        d = os.path.join(compiler.strpath, 'ucc', v)
        assert os.path.exists(d)
        ucc.join(v+'.py').write(m.family('compiler')+m.use(d))

        # write the mpi modules that unlock the mpi dependent modules

    ns = namespace()
    ns.core = core.strpath
    return ns


@pytest.mark.unit
def test_hierarchy(modules_path, mock_modulepath):
    """Just load and then unload a"""
    core_path = modules_path.core
    mp = mock_modulepath(modules_path.core)

    is_module = lambda x: pymod.modulepath.get(x) is not None

    for v in ('1.0', '2.0'):
        ucc = pymod.mc.load('ucc/'+v)
        assert ucc is not None
        d = os.path.normpath(os.path.join(core_path, '../compiler/ucc', v))
        print(d)
        assert os.path.isdir(d)
        assert pymod.modulepath.contains(d)
        a = pymod.modulepath.get('a')
        assert a is not None
        assert a.version.string == '1.0'

    return
