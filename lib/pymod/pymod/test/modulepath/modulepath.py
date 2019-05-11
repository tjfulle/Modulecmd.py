import os
import pytest
import pymod.paths
import pymod.modulepath
from contrib.util.itertools import groupby


basic_py_module = """\
setenv(self.name, '1')
prepend_path('PREPEND', self.version.string)
prepend_path('APPEND', self.version.string)
"""

basic_tcl_module = """\
#%Module1.0
setenv {0} 1
prepend-path PREPEND {1}
append-path APPEND {1}
"""

@pytest.fixture()
def modules_path(tmpdir):
    one = tmpdir.mkdir('1')
    one.join('a.py').write(basic_py_module)
    one.join('b.py').write(basic_py_module)

    py = one.mkdir('py')
    py.join('1.0.0.py').write(basic_py_module)
    py.join('2.0.0.py').write(basic_py_module)
    py.join('3.0.0.py').write(basic_py_module)
    default = py.join('default')
    default.mksymlinkto(py.join('2.0.0.py'))

    tcl = one.mkdir('tcl')
    tcl.join('1.0.0').write(basic_tcl_module.format('tcl', '1.0.0'))
    tcl.join('2.0.0').write(basic_tcl_module.format('tcl', '2.0.0'))
    tcl.join('3.0.0').write(basic_tcl_module.format('tcl', '3.0.0'))
    tcl.join('.version').write('set ModulesVersion "1.0.0"')

    ucc = one.mkdir('ucc')
    ucc.join('1.0.0.py').write(basic_py_module)
    ucc.join('2.0.0.py').write(basic_py_module)

    two = tmpdir.mkdir('2')
    ucc = two.mkdir('ucc')
    ucc.join('1.0.0.py').write(basic_py_module)
    ucc.join('4.0.0.py').write(basic_py_module)

    return tmpdir

def test_modulepath_available_1(modules_path, mock_modulepath):
    mp = mock_modulepath(modules_path.join('1').strpath)
    grouped = pymod.modulepath.group_by_modulepath()
    assert len(grouped) == 1
    _, modules = grouped[0]

    grouped = dict(groupby(modules, lambda x: x.name))

    a = grouped.pop('a')
    assert len(a) == 1
    assert not a[0].is_default
    assert a[0].type == pymod.module.python

    b = grouped.pop('b')
    assert len(b) == 1
    assert not b[0].is_default
    assert b[0].type == pymod.module.python

    py = grouped.pop('py')
    assert len(py) == 3
    for m in py:
        assert m.is_default if m.fullname == 'py/2.0.0' else not m.is_default
        assert m.type == pymod.module.python

    tcl = grouped.pop('tcl')
    assert len(tcl) == 3
    for m in tcl:
        assert m.is_default if m.fullname == 'tcl/1.0.0' else not m.is_default
        assert m.type == pymod.module.tcl

    ucc = grouped.pop('ucc')
    assert len(ucc) == 2
    for m in ucc:
        assert m.is_default if m.fullname == 'ucc/2.0.0' else not m.is_default
        assert m.type == pymod.module.python


def test_modulepath_get(modules_path, mock_modulepath):
    mp = mock_modulepath(modules_path.join('1').strpath)
    dirname = pymod.modulepath.mpath.path[0]

    module = pymod.modulepath.get('a')
    assert module.fullname == 'a'
    assert module.type == pymod.module.python
    assert module.filename == os.path.join(dirname, module.fullname + '.py')

    module = pymod.modulepath.get('b')
    assert module.fullname == 'b'
    assert module.type == pymod.module.python
    assert module.filename == os.path.join(dirname, module.fullname + '.py')

    module = pymod.modulepath.get('py')
    assert module.fullname == 'py/2.0.0'
    assert module.type == pymod.module.python
    assert module.filename == os.path.join(dirname, module.fullname + '.py')

    module = pymod.modulepath.get('tcl')
    assert module.fullname == 'tcl/1.0.0'
    assert module.type == pymod.module.tcl
    assert module.filename == os.path.join(dirname, module.fullname)

    module = pymod.modulepath.get('ucc')
    assert module.fullname == 'ucc/2.0.0'
    assert module.type == pymod.module.python
    assert module.filename == os.path.join(dirname, module.fullname + '.py')

    module = pymod.modulepath.get('ucc/1.0.0')
    assert module.fullname == 'ucc/1.0.0'
    assert module.type == pymod.module.python
    assert module.filename == os.path.join(dirname, module.fullname + '.py')

def test_modulepath_append_path(modules_path, mock_modulepath):

    mp = mock_modulepath(modules_path.join('1').strpath)
    d1 = pymod.modulepath.mpath.path[0]

    module = pymod.modulepath.get('ucc/1.0.0')
    assert module.fullname == 'ucc/1.0.0'
    assert module.filename == os.path.join(d1, module.fullname + '.py')

    module = pymod.modulepath.get('ucc')
    assert module.fullname == 'ucc/2.0.0'
    assert module.filename == os.path.join(d1, module.fullname + '.py')

    d2 = modules_path.join('2').strpath
    pymod.modulepath.append_path(d2)

    module = pymod.modulepath.get('ucc/1.0.0')
    assert module.fullname == 'ucc/1.0.0'
    assert module.filename == os.path.join(d1, module.fullname + '.py')

    module = pymod.modulepath.get('ucc')
    assert module.fullname == 'ucc/4.0.0'
    assert module.filename == os.path.join(d2, module.fullname + '.py')

    removed, _, _ = pymod.modulepath.remove_path(d2)
    assert len(removed) == 2
    removed_full_names = [m.fullname for m in removed]
    assert 'ucc/1.0.0' in removed_full_names
    assert 'ucc/4.0.0' in removed_full_names

    module = pymod.modulepath.get('ucc')
    assert module.fullname == 'ucc/2.0.0'
    assert module.filename == os.path.join(d1, module.fullname + '.py')

def test_modulepath_prepend_path(modules_path, mock_modulepath):
    mp = mock_modulepath(modules_path.join('1').strpath)
    d1 = pymod.modulepath.mpath.path[0]

    module = pymod.modulepath.get('ucc/1.0.0')
    assert module.fullname == 'ucc/1.0.0'
    assert module.filename == os.path.join(d1, module.fullname + '.py')

    module = pymod.modulepath.get('ucc')
    assert module.fullname == 'ucc/2.0.0'
    assert module.filename == os.path.join(d1, module.fullname + '.py')

    d2 = modules_path.join('2').strpath
    _, bumped = pymod.modulepath.prepend_path(d2)

    assert len(bumped) == 1
    assert bumped[0].fullname == 'ucc/1.0.0'

    module = pymod.modulepath.get('ucc/1.0.0')
    assert module.fullname == 'ucc/1.0.0'
    assert module.filename == os.path.join(d2, module.fullname + '.py')

    module = pymod.modulepath.get('ucc')
    assert module.fullname == 'ucc/4.0.0'
    assert module.filename == os.path.join(d2, module.fullname + '.py')

    removed, _, _ = pymod.modulepath.remove_path(d2)
    assert len(removed) == 2
    removed_full_names = [m.fullname for m in removed]
    assert 'ucc/1.0.0' in removed_full_names
    assert 'ucc/4.0.0' in removed_full_names

    module = pymod.modulepath.get('ucc/1.0.0')
    assert module.fullname == 'ucc/1.0.0'
    assert module.filename == os.path.join(d1, module.fullname + '.py')

    module = pymod.modulepath.get('ucc')
    assert module.fullname == 'ucc/2.0.0'
    assert module.filename == os.path.join(d1, module.fullname + '.py')
