import os
import pymod.paths
import pymod.modulepath
from contrib.util.itertools import groupby


class TestModulepath:
    def test_available_1(self):
        grouped = pymod.modulepath.group_by_modulepath()
        assert len(grouped) == 1
        dirname, modules = grouped[0]

        assert dirname == os.path.join(pymod.paths.mock_modulepath_path, 'core', '1')
        grouped = dict(groupby(modules, lambda x: x.name))

        a = grouped.pop('a')
        assert len(a) == 1
        assert not a[0].is_default
        assert a[0].type == 'PYTHON'

        b = grouped.pop('b')
        assert len(b) == 1
        assert not b[0].is_default
        assert b[0].type == 'PYTHON'

        ucc = grouped.pop('ucc')
        assert len(ucc) == 2
        for m in ucc:
            assert m.is_default if m.fullname == 'ucc/2.0.0' else not m.is_default
            assert m.type == 'PYTHON'

        pkg_a = grouped.pop('pkg-a')
        assert len(pkg_a) == 3
        for m in pkg_a:
            assert m.is_default if m.fullname == 'pkg-a/2.0.0' else not m.is_default
            assert m.type == 'PYTHON'

        pkg_b = grouped.pop('pkg-b')
        assert len(pkg_b) == 3
        for m in pkg_b:
            assert m.is_default if m.fullname == 'pkg-b/1.0.0' else not m.is_default
            assert m.type == 'TCL'

        pkg_c = grouped.pop('pkg-c')
        assert len(pkg_c) == 2
        for m in pkg_c:
            assert m.is_default if m.fullname == 'pkg-c/3.0.0' else not m.is_default
            assert m.type == 'PYTHON'

    def test_get(self):
        dirname = os.path.join(pymod.paths.mock_modulepath_path, 'core', '1')

        module = pymod.modulepath.get('a')
        assert module.fullname == 'a'
        assert module.type == 'PYTHON'
        assert module.filename == os.path.join(dirname, module.fullname + '.py')

        module = pymod.modulepath.get('b')
        assert module.fullname == 'b'
        assert module.type == 'PYTHON'
        assert module.filename == os.path.join(dirname, module.fullname + '.py')

        module = pymod.modulepath.get('ucc')
        assert module.fullname == 'ucc/2.0.0'
        assert module.type == 'PYTHON'
        assert module.filename == os.path.join(dirname, module.fullname + '.py')

        module = pymod.modulepath.get('ucc/1.0.0')
        assert module.fullname == 'ucc/1.0.0'
        assert module.type == 'PYTHON'
        assert module.filename == os.path.join(dirname, module.fullname + '.py')

        module = pymod.modulepath.get('pkg-a')
        assert module.fullname == 'pkg-a/2.0.0'
        assert module.type == 'PYTHON'
        assert module.filename == os.path.join(dirname, module.fullname + '.py')

        module = pymod.modulepath.get('pkg-b')
        assert module.fullname == 'pkg-b/1.0.0'
        assert module.type == 'TCL'
        assert module.filename == os.path.join(dirname, module.fullname)

        module = pymod.modulepath.get('pkg-c')
        assert module.fullname == 'pkg-c/3.0.0'
        assert module.type == 'PYTHON'
        assert module.filename == os.path.join(dirname, module.fullname + '.py')

    def test_append_path(self):
        d1 = os.path.join(pymod.paths.mock_modulepath_path, 'core', '1')
        d2 = os.path.join(pymod.paths.mock_modulepath_path, 'core', '2')

        module = pymod.modulepath.get('pkg-c/1.0.0')
        assert module.fullname == 'pkg-c/1.0.0'
        assert module.filename == os.path.join(d1, module.fullname + '.py')

        module = pymod.modulepath.get('pkg-c')
        assert module.fullname == 'pkg-c/3.0.0'
        assert module.filename == os.path.join(d1, module.fullname + '.py')

        pymod.modulepath.append_path(d2)

        module = pymod.modulepath.get('pkg-c/1.0.0')
        assert module.fullname == 'pkg-c/1.0.0'
        assert module.filename == os.path.join(d1, module.fullname + '.py')

        module = pymod.modulepath.get('pkg-c')
        assert module.fullname == 'pkg-c/4.0.0'
        assert module.filename == os.path.join(d2, module.fullname + '.py')

        removed = pymod.modulepath.remove_path(d2)
        assert len(removed) == 2
        removed_full_names = [m.fullname for m in removed]
        assert 'pkg-c/1.0.0' in removed_full_names
        assert 'pkg-c/4.0.0' in removed_full_names

        module = pymod.modulepath.get('pkg-c')
        assert module.fullname == 'pkg-c/3.0.0'
        assert module.filename == os.path.join(d1, module.fullname + '.py')

    def test_prepend_path(self):
        d1 = os.path.join(pymod.paths.mock_modulepath_path, 'core', '1')
        d2 = os.path.join(pymod.paths.mock_modulepath_path, 'core', '2')

        module = pymod.modulepath.get('pkg-c/1.0.0')
        assert module.fullname == 'pkg-c/1.0.0'
        assert module.filename == os.path.join(d1, module.fullname + '.py')

        module = pymod.modulepath.get('pkg-c')
        assert module.fullname == 'pkg-c/3.0.0'
        assert module.filename == os.path.join(d1, module.fullname + '.py')

        bumped = pymod.modulepath.prepend_path(d2)
        assert len(bumped) == 1
        assert bumped[0].fullname == 'pkg-c/1.0.0'

        module = pymod.modulepath.get('pkg-c/1.0.0')
        assert module.fullname == 'pkg-c/1.0.0'
        assert module.filename == os.path.join(d2, module.fullname + '.py')

        module = pymod.modulepath.get('pkg-c')
        assert module.fullname == 'pkg-c/4.0.0'
        assert module.filename == os.path.join(d2, module.fullname + '.py')

        removed = pymod.modulepath.remove_path(d2)
        assert len(removed) == 2
        removed_full_names = [m.fullname for m in removed]
        assert 'pkg-c/1.0.0' in removed_full_names
        assert 'pkg-c/4.0.0' in removed_full_names

        module = pymod.modulepath.get('pkg-c/1.0.0')
        assert module.fullname == 'pkg-c/1.0.0'
        assert module.filename == os.path.join(d1, module.fullname + '.py')

        module = pymod.modulepath.get('pkg-c')
        assert module.fullname == 'pkg-c/3.0.0'
        assert module.filename == os.path.join(d1, module.fullname + '.py')
