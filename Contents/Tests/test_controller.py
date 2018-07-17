import os
import pytest

import tools
from pymod.defaults import MP_KEY, LM_REFCNT_KEY
from pymod.controller import ModuleNotFoundError, InconsistentModuleState
from pymod.utils import str2dict


class TestController(tools.TestBase):

    @pytest.mark.unit
    @pytest.mark.modulepath
    def test_modulepath_append_a1(self):
        mc = tools.t_controller(modulepath='')
        d1 = tools.t_make_temp_directory(self.datadir)

        assert mc.modulepath.get_module_by_name('a') is None
        assert mc.modulepath.get_module_by_name('b') is None

        # Modify MODULEPATH and `a` and `b` will become available
        with open(os.path.join(d1, 'a.py'), 'w') as fh:
            fh.write("whatis('A descriptions')\n")
            fh.write('append_path("path", "/a/path")')
        with open(os.path.join(d1, 'b.py'), 'w') as fh:
            fh.write("whatis('A descriptions')\n")
            fh.write('append_path("path", "/b/path")')
        mc.append_path(MP_KEY, d1)
        assert d1 in mc.environ[MP_KEY].split(os.pathsep)

        assert mc.modulepath.get_module_by_name('a') is not None
        assert mc.modulepath.get_module_by_name('a') is not None

        # Load them
        mc.load('a')
        assert 'a' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == '/a/path'
        mc.load('b')
        assert 'b' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == '/a/path:/b/path'

    @pytest.mark.unit
    @pytest.mark.modulepath
    def test_modulepath_remove_a1(self):
        mc = tools.t_controller(modulepath='')

        d1 = tools.t_make_temp_directory(self.datadir)

        assert mc.modulepath.get_module_by_name('a') is None

        # Modify MODULEPATH and `a` and `b` will become available
        with open(os.path.join(d1, 'a.py'), 'w') as fh:
            fh.write('append_path("path", "/a/path")')
        mc.append_path(MP_KEY, d1)
        assert d1 in mc.environ[MP_KEY].split(os.pathsep)

        assert mc.modulepath.get_module_by_name('a') is not None

        # Load it
        mc.load('a')
        assert 'a' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == '/a/path'

        # Remove d1 from MODULEPATH and `a` should be removed and not available
        mc.remove_path(MP_KEY, d1)
        assert 'a' not in mc.environ.get_loaded_modules('names')
        assert mc.modulepath.get_module_by_name('a') is None
        assert mc.environ['path'] is None
        assert not bool(mc.environ[MP_KEY])

    @pytest.mark.unit
    @pytest.mark.modulepath
    def test_modulepath_remove_a2(self):
        mc = tools.t_controller(modulepath='')

        d1 = tools.t_make_temp_directory(self.datadir)
        d2 = tools.t_make_temp_directory(self.datadir)

        assert mc.modulepath.get_module_by_name('a') is None
        assert mc.modulepath.get_module_by_name('b') is None
        assert mc.modulepath.get_module_by_name('c') is None

        # Modify MODULEPATH and `a` and `b` will become available
        with open(os.path.join(d1, 'a.py'), 'w') as fh:
            fh.write('append_path("path", "/a/path")')
        with open(os.path.join(d1, 'b.py'), 'w') as fh:
            fh.write('append_path("path", "/b/path")\n'
                     'append_path("MODULEPATH", "{0}")'.format(d2))
        with open(os.path.join(d2, 'c.py'), 'w') as fh:
            fh.write('append_path("path", "/c/path")')

        mc.append_path(MP_KEY, d1)
        assert d1 in mc.environ[MP_KEY].split(os.pathsep)
        assert d1 == mc.environ[MP_KEY].split(os.pathsep)[0]

        # Load them
        assert mc.modulepath.get_module_by_name('a') is not None
        mc.load('a')
        assert 'a' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == '/a/path'

        assert mc.modulepath.get_module_by_name('b') is not None
        m = mc.load('b')
        assert 'b' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == '/a/path:/b/path'
        assert d2 in mc.environ[MP_KEY].split(os.pathsep)
        assert d2 == mc.environ[MP_KEY].split(os.pathsep)[1]

        assert mc.modulepath.get_module_by_name('c') is not None
        mc.load('c')
        assert 'c' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == '/a/path:/b/path:/c/path'

        # Remove d1 from MODULEPATH and `a`, `b`, and `c` should be
        # removed and not available
        mc.remove_path(MP_KEY, d1)
        assert 'a' not in mc.environ.get_loaded_modules('names')
        assert 'b' not in mc.environ.get_loaded_modules('names')
        assert 'c' not in mc.environ.get_loaded_modules('names')
        assert mc.modulepath.get_module_by_name('a') is None
        assert mc.modulepath.get_module_by_name('b') is None
        assert mc.modulepath.get_module_by_name('c') is None
        assert mc.environ['path'] is None

    @pytest.mark.unit
    @pytest.mark.modulepath
    def test_modulepath_remove_a3(self):
        mc = tools.t_controller(modulepath='')

        d1 = tools.t_make_temp_directory(self.datadir)
        d2 = tools.t_make_temp_directory(self.datadir)
        d3 = tools.t_make_temp_directory(self.datadir)
        d4 = tools.t_make_temp_directory(self.datadir)

        assert mc.modulepath.get_module_by_name('a') is None
        assert mc.modulepath.get_module_by_name('b') is None
        assert mc.modulepath.get_module_by_name('c') is None
        assert mc.modulepath.get_module_by_name('d') is None

        # Write modulefiles
        with open(os.path.join(d1, 'a.py'), 'w') as fh:
            fh.write('append_path("path", "/a/path")')
        with open(os.path.join(d1, 'b.py'), 'w') as fh:
            fh.write('append_path("path", "/b/path")\n'
                     'append_path("MODULEPATH", "{0}")'.format(d2))
        with open(os.path.join(d2, 'c.py'), 'w') as fh:
            fh.write('append_path("path", "/c/path")\n'
                     'append_path("MODULEPATH", "{0}")'.format(d3))
        with open(os.path.join(d3, 'd.py'), 'w') as fh:
            fh.write('append_path("path", "/d/path")\n'
                     'append_path("MODULEPATH", "{0}")'.format(d4))
        with open(os.path.join(d4, 'e.py'), 'w') as fh:
            fh.write('append_path("path", "/e/path")')

        # Modify MODULEPATH and `a` and `b` will become available
        mc.append_path(MP_KEY, d1)
        assert d1 in mc.environ[MP_KEY].split(os.pathsep)

        # Load them
        assert mc.modulepath.get_module_by_name('a') is not None
        mc.load('a')
        assert 'a' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == '/a/path'

        assert mc.modulepath.get_module_by_name('b') is not None
        m = mc.load('b')
        assert 'b' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == '/a/path:/b/path'
        assert d2 in mc.environ[MP_KEY].split(os.pathsep)

        assert mc.modulepath.get_module_by_name('c') is not None
        mc.load('c')
        assert 'c' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == '/a/path:/b/path:/c/path'
        assert d3 in mc.environ[MP_KEY].split(os.pathsep)

        assert mc.modulepath.get_module_by_name('d') is not None
        mc.load('d')
        assert 'd' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == '/a/path:/b/path:/c/path:/d/path'
        assert d4 in mc.environ[MP_KEY].split(os.pathsep)

        mc.load('e')
        assert 'e' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == '/a/path:/b/path:/c/path:/d/path:/e/path'

        # Remove odir from MODULEPATH and `first`, `second`, `third`, `fourth`, and
        # `fifth should be removed and not available
        mc.remove_path(MP_KEY, d1)
        assert 'a' not in mc.environ.get_loaded_modules('names')
        assert 'b' not in mc.environ.get_loaded_modules('names')
        assert 'c' not in mc.environ.get_loaded_modules('names')
        assert 'd' not in mc.environ.get_loaded_modules('names')
        assert 'e' not in mc.environ.get_loaded_modules('names')
        assert mc.modulepath.get_module_by_name('a') is None
        assert mc.modulepath.get_module_by_name('b') is None
        assert mc.modulepath.get_module_by_name('c') is None
        assert mc.modulepath.get_module_by_name('d') is None
        assert mc.modulepath.get_module_by_name('e') is None
        assert mc.environ['path'] is None

    @pytest.mark.unit
    @pytest.mark.modulepath
    def test_modulepath_remove_a4(self):
        mc = tools.t_controller(modulepath='')

        d1 = tools.t_make_temp_directory(self.datadir)
        d2 = tools.t_make_temp_directory(self.datadir)
        d3 = tools.t_make_temp_directory(self.datadir)

        assert mc.modulepath.get_module_by_name('a') is None
        assert mc.modulepath.get_module_by_name('b') is None

        # Write modulefiles
        with open(os.path.join(d1, 'a1.py'), 'w') as fh:
            fh.write('append_path("path", "a-1")\n'
                     'append_path("MODULEPATH", "{0}")'.format(d2))
        with open(os.path.join(d1, 'a2.py'), 'w') as fh:
            fh.write('prepend_path("MODULEPATH", "{0}")\n'.format(d3))
            fh.write('append_path("path", "a-2")')

        with open(os.path.join(d2, 'b.py'), 'w') as fh:
            fh.write('append_path("path", "b-1")')
        with open(os.path.join(d3, 'b.py'), 'w') as fh:
            fh.write('append_path("path", "b-2")')

        # Modify MODULEPATH and `a` and `b` will become available
        mc.append_path(MP_KEY, d1)
        assert d1 in mc.environ[MP_KEY].split(os.pathsep)

        # Load them
        assert mc.modulepath.get_module_by_name('a1') is not None
        mc.load('a1')
        assert 'a1' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == 'a-1'
        assert mc.modulepath.path[-1] == d2

        assert mc.modulepath.get_module_by_name('b') is not None
        m = mc.load('b')
        assert 'b' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == 'a-1:b-1'

        mc.load('a2')
        assert mc.modulepath.path[0] == d3
        assert mc.environ['path'] == 'a-1:b-2:a-2'

        mc.unload('a2')
        assert d3 not in mc.modulepath
        assert mc.environ['path'] == 'a-1:b-1'

    @pytest.mark.unit
    @pytest.mark.modulepath
    def test_modulepath_remove_a5(self):
        mc = tools.t_controller(modulepath='')

        d1 = tools.t_make_temp_directory(self.datadir)
        d2 = tools.t_make_temp_directory(self.datadir)
        d3 = tools.t_make_temp_directory(self.datadir)
        d4 = tools.t_make_temp_directory(self.datadir)

        assert mc.modulepath.get_module_by_name('a') is None
        assert mc.modulepath.get_module_by_name('b') is None
        assert mc.modulepath.get_module_by_name('c') is None

        # Write modulefiles
        with open(os.path.join(d1, 'a.py'), 'w') as fh:
            fh.write('append_path("path", "/a/path")\n'
                     'append_path("MODULEPATH", "{0}")'.format(d2))
        with open(os.path.join(d2, 'b.py'), 'w') as fh:
            fh.write('append_path("path", "/b-1/path")\n'
                     'append_path("MODULEPATH", "{0}")'.format(d3))
        with open(os.path.join(d3, 'c.py'), 'w') as fh:
            fh.write('prepend_path("MODULEPATH", "{0}")\n'.format(d4))
            fh.write('append_path("path", "/c/path")')
        with open(os.path.join(d4, 'b.py'), 'w') as fh:
            fh.write('append_path("path", "/b-2/path")\n')

        # Modify MODULEPATH and `a` and `b` will become available
        mc.append_path(MP_KEY, d1)
        assert d1 in mc.environ[MP_KEY].split(os.pathsep)

        # Load them
        assert mc.modulepath.get_module_by_name('a') is not None
        mc.load('a')
        assert 'a' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == '/a/path'
        assert d2 in mc.environ[MP_KEY].split(os.pathsep)

        assert mc.modulepath.get_module_by_name('b') is not None
        m = mc.load('b')
        assert 'b' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == '/a/path:/b-1/path'
        assert d3 in mc.environ[MP_KEY].split(os.pathsep)

        # In this test:
        #  a puts b on MODULEPATH
        #  b puts c on MODULEPATH
        #  c changes MODULEPATH so that another b is picked up
        #    the process of picking up the other b is to remove the first b
        #    and load the second.  The process of unloading the first will
        #    then modify MODULEPATH so that c is not longer on MODULEPATH,
        #    resulting in an inconsistent state.
        assert mc.modulepath.get_module_by_name('c') is not None
        try:
            mc.load('c')
            assert True, "This should have raised InconsistentModuleState!"
        except InconsistentModuleState:
            pass

    @pytest.mark.unit
    @pytest.mark.modulepath
    def test_modulepath_prepend_b1(self):

        mc = tools.t_controller(modulepath='')
        d1 = tools.t_make_temp_directory(self.datadir)

        assert mc.modulepath.get_module_by_name('a') is None
        assert mc.modulepath.get_module_by_name('b') is None

        # Write modulefiles
        with open(os.path.join(d1, 'a.py'), 'w') as fh:
            fh.write('append_path("path", "/a/path")')
        with open(os.path.join(d1, 'b.py'), 'w') as fh:
            fh.write('prepend_path("path", "/b/path")')

        # Modify MODULEPATH and `a` and `b` will become available
        mc.append_path(MP_KEY, d1)
        assert d1 in mc.environ[MP_KEY].split(os.pathsep)
        assert mc.modulepath.get_module_by_name('a') is not None
        assert mc.modulepath.get_module_by_name('b') is not None

        # Load it
        mc.load('a')
        assert 'a' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == '/a/path'

        mc.load('b')
        assert 'b' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == '/b/path:/a/path'

    @pytest.mark.unit
    @pytest.mark.modulepath
    def test_modulepath_prepend_b2(self):

        mc = tools.t_controller(modulepath='')
        d1 = tools.t_make_temp_directory(self.datadir)
        ucc_1 = os.path.join(d1, 'ucc')
        tools.t_make_directory(ucc_1)

        d2 = tools.t_make_temp_directory(self.datadir)
        ucc_2 = os.path.join(d2, 'ucc')
        tools.t_make_directory(ucc_2)

        assert mc.modulepath.get_module_by_name('b') is None
        assert mc.modulepath.get_module_by_name('ucc') is None

        # Write modulefiles
        with open(os.path.join(ucc_1, '1.0.py'), 'w') as fh:
            fh.write('setenv("ENVAR", "1")')
        with open(os.path.join(d1, 'b.py'), 'w') as fh:
            fh.write('append_path("path", "/a/path")\n'
                     'prepend_path("MODULEPATH", "{0}")'.format(d2))
        with open(os.path.join(ucc_2, '1.0.py'), 'w') as fh:
            fh.write('setenv("ENVAR", "2")')

        # Modify MODULEPATH and `first` will become available
        mc.append_path(MP_KEY, d1)
        assert d1 == mc.environ[MP_KEY].split(os.pathsep)[-1]

        m1 = mc.modulepath.get_module_by_name('ucc')
        assert m1 is not None

        # Load it
        mc.load('ucc')
        assert mc.environ['ENVAR'] == '1'

        mc.load('b')
        assert d2 in mc.environ[MP_KEY].split(os.pathsep)
        assert mc.environ['ENVAR'] == '2'

        m2 = mc.modulepath.get_module_by_name('ucc')
        s = mc.m_state_changed['MP']['Up'][0]

        assert s[0].filename == m1.filename
        assert s[1].filename == m2.filename

    @pytest.mark.unit
    @pytest.mark.modulepath
    def test_modulepath_prepend_b3(self):

        mc = tools.t_controller(modulepath='')
        d1 = tools.t_make_temp_directory(self.datadir)
        d2 = tools.t_make_temp_directory(self.datadir)

        assert mc.modulepath.get_module_by_name('a') is None
        assert mc.modulepath.get_module_by_name('b') is None

        # Write modulefiles
        with open(os.path.join(d1, 'a.py'), 'w') as fh:
            fh.write('append_path("path", "/a1/path")')
        with open(os.path.join(d2, 'a.py'), 'w') as fh:
            fh.write('prepend_path("path", "/a2/path")')

        # Modify MODULEPATH and `a` and `b` will become available
        mc.append_path(MP_KEY, d1)
        assert d1 in mc.environ[MP_KEY].split(os.pathsep)
        assert mc.modulepath.get_module_by_name('a') is not None

        # Load it
        mc.load('a')
        assert 'a' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == '/a1/path'

        mc.prepend_path(MP_KEY, d2)
        assert 'a' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == '/a2/path'

        assert mc.m_state_changed.get('MP') is not None
        mc.report_changed_module_state()

    @pytest.mark.unit
    @pytest.mark.modulepath
    def test_modulepath_remove_b2(self):
        mc = tools.t_controller(modulepath='')

        d1 = tools.t_make_temp_directory(self.datadir)
        d2 = tools.t_make_temp_directory(self.datadir)
        d3 = tools.t_make_temp_directory(self.datadir)
        d4 = tools.t_make_temp_directory(self.datadir)

        assert mc.modulepath.get_module_by_name('a') is None
        assert mc.modulepath.get_module_by_name('b') is None
        assert mc.modulepath.get_module_by_name('c') is None
        assert mc.modulepath.get_module_by_name('d') is None

        # Write modulefiles
        with open(os.path.join(d1, 'a.py'), 'w') as fh:
            fh.write('append_path("path", "/a/path")')
        with open(os.path.join(d1, 'b.py'), 'w') as fh:
            fh.write('prepend_path("path", "/b/path")\n'
                     'prepend_path("MODULEPATH", "{0}")'.format(d2))
        with open(os.path.join(d2, 'c.py'), 'w') as fh:
            fh.write('prepend_path("path", "/c/path")\n'
                     'prepend_path("MODULEPATH", "{0}")'.format(d3))
        with open(os.path.join(d3, 'd.py'), 'w') as fh:
            fh.write('prepend_path("path", "/d/path")\n'
                     'prepend_path("MODULEPATH", "{0}")'.format(d4))
        with open(os.path.join(d4, 'e.py'), 'w') as fh:
            fh.write('prepend_path("path", "/e/path")')

        # Modify MODULEPATH and `a` and `b` will become available
        mc.append_path(MP_KEY, d1)
        assert d1 in mc.environ[MP_KEY].split(os.pathsep)

        # Load them
        assert mc.modulepath.get_module_by_name('a') is not None
        mc.load('a')
        assert 'a' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == '/a/path'

        assert mc.modulepath.get_module_by_name('b') is not None
        m = mc.load('b')
        assert 'b' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == '/b/path:/a/path'
        assert d2 == mc.environ[MP_KEY].split(os.pathsep)[0]

        assert mc.modulepath.get_module_by_name('c') is not None
        mc.load('c')
        assert 'c' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == '/c/path:/b/path:/a/path'
        assert d3 == mc.environ[MP_KEY].split(os.pathsep)[0]

        assert mc.modulepath.get_module_by_name('d') is not None
        mc.load('d')
        assert 'd' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == '/d/path:/c/path:/b/path:/a/path'
        assert d4 == mc.environ[MP_KEY].split(os.pathsep)[0]

        mc.load('e')
        assert 'e' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == '/e/path:/d/path:/c/path:/b/path:/a/path'

        # Remove odir from MODULEPATH and `first`, `second`, `third`, `fourth`, and
        # `fifth should be removed and not available
        mc.remove_path(MP_KEY, d1)
        assert 'a' not in mc.environ.get_loaded_modules('names')
        assert 'b' not in mc.environ.get_loaded_modules('names')
        assert 'c' not in mc.environ.get_loaded_modules('names')
        assert 'd' not in mc.environ.get_loaded_modules('names')
        assert 'e' not in mc.environ.get_loaded_modules('names')
        assert mc.modulepath.get_module_by_name('a') is None
        assert mc.modulepath.get_module_by_name('b') is None
        assert mc.modulepath.get_module_by_name('c') is None
        assert mc.modulepath.get_module_by_name('d') is None
        assert mc.modulepath.get_module_by_name('e') is None
        assert mc.environ['path'] is None

    @pytest.mark.unit
    @pytest.mark.modulepath
    def test_modulepath_swap(self):
        """In this test a1 changes MODULEPATH so that b is available and
        b changes MODULEPATH so that c is available.  a1 is swapped for a2 and
        a different b is made available and loaded."""

        mc = tools.t_controller(modulepath='')

        d1 = tools.t_make_temp_directory(self.datadir)
        d2 = tools.t_make_temp_directory(self.datadir)
        d3 = tools.t_make_temp_directory(self.datadir)
        d4 = tools.t_make_temp_directory(self.datadir)
        d5 = tools.t_make_temp_directory(self.datadir)
        d6 = tools.t_make_temp_directory(self.datadir)

        assert mc.modulepath.get_module_by_name('a1') is None
        assert mc.modulepath.get_module_by_name('a2') is None
        assert mc.modulepath.get_module_by_name('b') is None
        assert mc.modulepath.get_module_by_name('c') is None

        # Write modulefiles
        with open(os.path.join(d1, 'a1.py'), 'w') as fh:
            fh.write('append_path("path", "a1")\n'
                     'append_path("MODULEPATH", "{0}")'.format(d2))
        with open(os.path.join(d2, 'b.py'), 'w') as fh:
            fh.write('append_path("path", "b-a1")\n'
                     'append_path("MODULEPATH", "{0}")'.format(d3))
        with open(os.path.join(d3, 'c.py'), 'w') as fh:
            fh.write('append_path("path", "c-a1")\n'
                     'append_path("MODULEPATH", "{0}")'.format(d4))
        with open(os.path.join(d3, 'd.py'), 'w') as fh:
            fh.write('append_path("path", "d-a1")\n')

        # Write modulefiles
        with open(os.path.join(d1, 'a2.py'), 'w') as fh:
            fh.write('append_path("path", "a2")\n'
                     'append_path("MODULEPATH", "{0}")'.format(d5))
        with open(os.path.join(d5, 'b.py'), 'w') as fh:
            fh.write('append_path("path", "b-a2")\n'
                     'append_path("MODULEPATH", "{0}")'.format(d6))
        with open(os.path.join(d6, 'c.py'), 'w') as fh:
            fh.write('append_path("path", "c-a2")\n')


        # Modify MODULEPATH and `a` and `b` will become available
        mc.append_path(MP_KEY, d1)
        assert d1 in mc.environ[MP_KEY].split(os.pathsep)

        # Load them
        assert mc.modulepath.get_module_by_name('a1') is not None
        mc.load('a1')
        assert 'a1' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == 'a1'
        assert d2 in mc.environ[MP_KEY].split(os.pathsep)

        assert mc.modulepath.get_module_by_name('b') is not None
        m = mc.load('b')
        assert 'b' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == 'a1:b-a1'
        assert d3 in mc.environ[MP_KEY].split(os.pathsep)

        assert mc.modulepath.get_module_by_name('c') is not None
        mc.load('c')
        assert 'c' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == 'a1:b-a1:c-a1'
        assert d4 in mc.environ[MP_KEY].split(os.pathsep)

        assert mc.modulepath.get_module_by_name('d') is not None
        mc.load('d')
        assert 'd' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == 'a1:b-a1:c-a1:d-a1'

        mc.swap('a1', 'a2')
        assert 'a2' in mc.environ.get_loaded_modules('names')
        assert 'b' in mc.environ.get_loaded_modules('names')
        assert 'c' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == 'a2:b-a2:c-a2'

        # Nothing should happen, a1 is not loaded so no swap occurs
        mc.swap('a1', 'a2')
        assert mc.environ['path'] == 'a2:b-a2:c-a2'

        # Nothing should happen.  a1 and a2 are both loaded, no swap occurs
        mc.load('a1')
        assert mc.environ['path'] == 'a2:b-a2:c-a2:a1'
        mc.swap('a1', 'a2')

        try:
            mc.swap('a2', 'fake')
            assert False
        except ModuleNotFoundError:
            pass

        try:
            mc.swap('fake', 'a1')
            assert False
        except ModuleNotFoundError:
            pass

    def test_duplicates_in_modulepath(self):
        d1 = tools.t_make_temp_directory(self.datadir)
        d2 = tools.t_make_temp_directory(self.datadir)
        d3 = tools.t_make_temp_directory(self.datadir)
        mc = tools.t_controller(modulepath=':'.join((d1, d1, d1)))
        b = 'foo' in mc
        f = os.path.join(d2, 'a1.py')
        with open(f, 'w') as fh:
            fh.write('append_path("path", "a1")\n')
        mc.create_module_from_filename(f)

        f = os.path.join(d3, 'a2.py')
        with open(f, 'w') as fh:
            fh.write('append_path("path", "a2")\n')
        m = mc.get_module(f)

        try:
            m = mc.get_module('a8', raise_ex=1)
            assert False
        except ModuleNotFoundError:
            pass

        assert mc.get('foo') is None

        m = mc.get_module('a1')
        assert m is not None
        mc.environ.set_loaded_modules('names', [])
        mc.environ.set_loaded_modules('filenames', [m.filename])
        try:
            mc.add_module(m)
            assert False
        except:
            pass

        m = mc.get_module('a1')
        assert m is not None
        mc.environ.set_loaded_modules('names', [m.fullname])
        mc.environ.set_loaded_modules('filenames', [])
        try:
            mc.add_module(m)
            assert False
        except:
            pass

        m = mc.get_module('a1')
        assert m is not None
        mc.environ.set_loaded_modules('names', [m.fullname])
        mc.environ.set_loaded_modules('filenames', [''])
        try:
            mc.remove_module(m)
            assert False
        except:
            pass

        m = mc.get_module('a1')
        assert m is not None
        mc.environ.set_loaded_modules('names', [])
        mc.environ.set_loaded_modules('filenames', [m.filename])
        try:
            mc.remove_module(m)
            assert False
        except:
            pass

        f = os.path.join(d2, 'a/2.py')
        os.makedirs(os.path.join(d2, 'a'))
        with open(f, 'w') as fh:
            fh.write('append_path("path", "a/2")\n')
        mc.create_module_from_filename(f)
        m = mc.get_module('a/2')
        m.fullname = 'a/2'
        mc.moduleopts[m.name] = {'foo': 'bar'}
        assert mc.get_moduleopts(m) == {'foo': 'bar'}

    def test_cb_swap(self):

        d1 = tools.t_make_temp_directory(self.datadir)
        with open(os.path.join(d1, 'a.py'), 'w') as fh:
            fh.write('append_path("path", "/a/path")')

        d2 = tools.t_make_temp_directory(self.datadir)
        with open(os.path.join(d2, 'b.py'), 'w') as fh:
            fh.write('append_path("path", "/b/path")')

        mc = tools.t_controller(modulepath=':'.join([d1, d2]))

        mc.load('a')
        assert 'a' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == '/a/path'
        mc.cb_swap('load', 'a', 'b')
        assert 'b' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == '/b/path'

        try:
            mc.cb_swap('load', 'b', 'c')
            assert False
        except ModuleNotFoundError:
            pass

        try:
            mc.cb_swap('load', 'c', 'a')
            assert False
        except ModuleNotFoundError:
            pass

        mc.load('a')
        mc.cb_swap('load', 'b', 'a')

        mc.unload('a')
        mc.unload('b')
        mc.cb_swap('load', 'a', 'b')

        mc.cb_swap('unload', 'a', 'b')

    def test_cb_load(self):

        d1 = tools.t_make_temp_directory(self.datadir)
        with open(os.path.join(d1, 'a.py'), 'w') as fh:
            fh.write('append_path("path", "/a/path")')

        d2 = tools.t_make_temp_directory(self.datadir)
        with open(os.path.join(d2, 'b.py'), 'w') as fh:
            fh.write('append_path("path", "/b/path")')

        mc = tools.t_controller(modulepath=':'.join([d1, d2]))
        mc.cb_load('load', load_first_of=('a', 'b'))
        assert mc.get_module('a').is_loaded
        mc.cb_load('pop', 'a')
        assert mc.get_module('a').is_loaded
        assert mc.cb_is_loaded('a')
        mc.unload('a')
        assert not mc.get_module('a').is_loaded
        mc.cb_load('load', 'b')
        assert mc.get_module('b').is_loaded
        mc.cb_load('unload', 'b')
        assert not mc.get_module('b').is_loaded

        try:
            mc.cb_load('load', load_first_of=('c', 'd', 'e'))
            assert False
        except ModuleNotFoundError:
            pass

        mc.cb_load('load', load_first_of=('c', 'd', 'e', None))

    def test_cb_unload(self):

        d1 = tools.t_make_temp_directory(self.datadir)
        with open(os.path.join(d1, 'a.py'), 'w') as fh:
            fh.write('append_path("path", "/a/path")')

        d2 = tools.t_make_temp_directory(self.datadir)
        with open(os.path.join(d2, 'b.py'), 'w') as fh:
            fh.write('append_path("path", "/b/path")')

        mc = tools.t_controller(modulepath=':'.join([d1, d2]))

        # Load 'a' twice to increment it's reference count
        mc.load('a')
        mc.cb_load('load', 'a')
        assert mc.get_module('a').is_loaded
        mc.cb_unload('unload', 'a')
        assert mc.get_module('a').is_loaded

        # Since 'a' was loaded twice, it's reference count must be decremented
        # before unloading
        mc.cb_unload('load', 'a')
        assert mc.get_module('a').is_loaded
        mc.cb_unload('load', 'a')
        assert not mc.get_module('a').is_loaded
        assert mc.cb_unload('load', 'x') is None

    def test_cb_use(self):

        d1 = tools.t_make_temp_directory(self.datadir)
        with open(os.path.join(d1, 'a.py'), 'w') as fh:
            fh.write('append_path("path", "/a/path")')

        d2 = tools.t_make_temp_directory(self.datadir)
        with open(os.path.join(d2, 'b.py'), 'w') as fh:
            fh.write('append_path("path", "/b/path")')

        mc = tools.t_controller(modulepath=d1)
        mc.load('a')
        assert mc.get_module('a').is_loaded
        mc.cb_use(d2)
        mc.load('b')
        assert mc.get_module('b').is_loaded

        mc.cb_unuse(d2)
        assert mc.get_module('b') is None
