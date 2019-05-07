import pytest
import os
import sys

import tools
from pymod.defaults import MP_KEY, LM_KEY
from pymod.utils import dict2str
from pymod.controller import ModuleNotFoundError

class TestLoadUnload(tools.TestBase):

    def write_modules_a_b(self, do_not_register=None):
        d1 = tools.t_make_temp_directory(self.datadir)
        with open(os.path.join(d1, 'a.py'), 'w') as fh:
            fh.write("# pymod: enable_if=True")
            if do_not_register:
                fh.write(', do_not_register=True')
            fh.write('\n')
            fh.write("whatis('A descriptions')\n")
            fh.write("setenv('envar1', 'val1')\nsetenv('envar2', 'val2')\n")
            fh.write("append_path('path', '/c/path', '/d/path')\n")
            fh.write("remove_path('key', '/d/path')\n")
            fh.write("set_alias('alias', 'ls')\n")
            fh.write("set_shell_function('function', 'ls $@')")
        with open(os.path.join(d1, 'b.py'), 'w') as fh:
            fh.write("""load('a')""")
        with open(os.path.join(d1, 'c.py'), 'w') as fh:
            fh.write("""load_first('x', 'a', 'b')""")
        with open(os.path.join(d1, 'd.py'), 'w') as fh:
            fh.write("""load_first('-', '^', '&', None)""")
        with open(os.path.join(d1, 'e.py'), 'w') as fh:
            fh.write("""unload('a')""")
        with open(os.path.join(d1, 'f.py'), 'w') as fh:
            fh.write("""unload('&')""")
        return d1

    @pytest.mark.sandbox
    def test_exec_load_1(self):
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1,
                          path='/a/path:/b/path',
                          key='/c/path:/d/path')
        a = mc.load('a')
        assert a.metadata['enable_if'] == True
        assert mc['envar1'] == 'val1'
        assert mc['envar2'] == 'val2'
        assert mc['path'] == '/a/path:/b/path:/c/path:/d/path'
        assert mc['key'] == '/c/path'
        assert mc[LM_KEY] == 'a'
        assert mc.modulepath.get_module_by_name('a').is_loaded

    @pytest.mark.sandbox
    def test_exec_load_2(self):
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1,
                          path='/a/path:/b/path',
                          key='/c/path:/d/path')
        # use loadfile instead of load('b')
        mc.loadfile(os.path.join(d1, 'b.py'))
        assert mc['envar1'] == 'val1'
        assert mc['envar2'] == 'val2'
        assert mc['path'] == '/a/path:/b/path:/c/path:/d/path'
        assert mc['key'] == '/c/path'
        assert mc[LM_KEY] == 'a:b'
        assert mc.modulepath.get_module_by_name('a').is_loaded
        assert mc.modulepath.get_module_by_name('b').is_loaded
        mc.dump()
        mc.unload('b')
        assert not mc.modulepath.get_module_by_name('b').is_loaded
        mc.unload('a')
        assert not mc.modulepath.get_module_by_name('a').is_loaded
        mc.dump()

    @pytest.mark.sandbox
    def test_exec_load_then_unload(self):
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1)
        # use loadfile instead of load('b')
        mc.loadfile(os.path.join(d1, 'b.py'))
        assert mc[LM_KEY] == 'a:b'
        assert mc.modulepath.get_module_by_name('a').is_loaded
        assert mc.modulepath.get_module_by_name('b').is_loaded
        mc.dump()
        mc.load('e')
        assert not mc.modulepath.get_module_by_name('a').is_loaded
        mc.unload('e')
        mc.load('f')

    @pytest.mark.sandbox
    def test_exec_load_then_unload(self):
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1)
        # use loadfile instead of load('b')
        mc.loadfile(os.path.join(d1, 'b.py'))
        assert mc[LM_KEY] == 'a:b'
        assert mc.modulepath.get_module_by_name('a').is_loaded
        assert mc.modulepath.get_module_by_name('b').is_loaded
        mc.dump()
        mc.load('e')
        assert not mc.modulepath.get_module_by_name('a').is_loaded
        mc.unload('e')
        mc.load('f')

    @pytest.mark.sandbox
    def test_exec_load_use_unuse(self):
        d1 = tools.t_make_temp_directory(self.datadir)
        d2 = tools.t_make_temp_directory(d1)
        with open(os.path.join(d1, 'g.py'), 'w') as fh:
            fh.write("""use('{0}')""".format(d2))
        with open(os.path.join(d1, 'h.py'), 'w') as fh:
            fh.write("""unuse('{0}')""".format(d2))
        mc = tools.t_controller(modulepath=d1)
        # use loadfile instead of load('b')
        mc.loadfile(os.path.join(d1, 'g.py'))
        assert mc[LM_KEY] == 'g'
        assert mc[MP_KEY] == d2 + os.pathsep + d1
        mc.loadfile(os.path.join(d1, 'h.py'))
        assert mc[MP_KEY] == d1

    @pytest.mark.sandbox
    def test_exec_load_first_of(self):
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1,
                          path='/a/path:/b/path',
                          key='/c/path:/d/path')
        mc.load('c')
        assert mc['envar1'] == 'val1'
        assert mc['envar2'] == 'val2'
        assert mc['path'] == '/a/path:/b/path:/c/path:/d/path'
        assert mc['key'] == '/c/path'
        assert mc[LM_KEY] == 'a:c'
        assert mc.modulepath.get_module_by_name('a').is_loaded

    @pytest.mark.sandbox
    def test_exec_load_first_of_2(self):
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1,
                          path='/a/path:/b/path',
                          key='/c/path:/d/path')
        mc.load('d')
        assert mc['path'] == '/a/path:/b/path'
        assert mc['key'] == '/c/path:/d/path'
        mc.load('d')

    @pytest.mark.sandbox
    def test_exec_load_not_found(self):
        d1 = tools.t_make_temp_directory(self.datadir)
        d2 = tools.t_make_temp_directory(d1)
        with open(os.path.join(d1, 'aaxx.py'), 'w') as fh:
            fh.write("whatis('A descriptions')\n")
            fh.write("setenv('envar1', 'val1')")
        with open(os.path.join(d2, '1.0.py'), 'w') as fh:
            fh.write("whatis('A descriptions')\n")
            fh.write("setenv('envar1', 'val1')")
        with open(os.path.join(d2, '2.0.py'), 'w') as fh:
            fh.write("whatis('A descriptions')\n")
            fh.write("setenv('envar1', 'val1')")
        mc = tools.t_controller(modulepath=d1)
        try:
            mc.load('axx')
            assert False, 'unknown module loaded without error!'
        except ModuleNotFoundError:
            pass
        try:
            mc.load('axx.py')
            assert False, 'unknown module loaded without error!'
        except ModuleNotFoundError:
            pass
        try:
            name = os.path.basename(d2)
            mc.load(name[:-2])
            assert False, 'unknown module loaded without error!'
        except ModuleNotFoundError:
            pass
        try:
            mc.load(d2[:-2])
            assert False, 'unknown module loaded without error!'
        except ModuleNotFoundError:
            pass
        try:
            mc.loadfile('foo')
            assert False, 'unknown modulefile loaded without error!'
        except ModuleNotFoundError:
            pass

    def test_exec_load_ld_library_path(self):
        d1 = tools.t_make_temp_directory(self.datadir)
        with open(os.path.join(d1, 'a.py'), 'w') as fh:
            fh.write("setenv('LD_LIBRARY_PATH', 'B')\n")
            fh.write("append_path('LD_LIBRARY_PATH', 'C')\n")
            fh.write("prepend_path('LD_LIBRARY_PATH', 'A')\n")
        with open(os.path.join(d1, 'b.py'), 'w') as fh:
            fh.write("unsetenv('LD_LIBRARY_PATH')")
        mc = tools.t_controller(modulepath=d1)
        mc.load('a')
        expected = 'A:B:C'
        if 'darwin' in sys.platform.lower():
            assert mc['DYLD_LIBRARY_PATH'] == expected
        else:
            assert mc['LD_LIBRARY_PATH'] == expected
        mc.load('b')
        if 'darwin' in sys.platform.lower():
            assert mc['DYLD_LIBRARY_PATH'] is None
        else:
            assert mc['LD_LIBRARY_PATH'] is None

    @pytest.mark.sandbox
    def test_exec_unload_1(self):
        d1 = self.write_modules_a_b()
        mc = tools.t_controller(modulepath=d1,
                          envar1='val1', envar2='val2',
                          path='/a/path:/b/path:/c/path:/d/path',
                          key='/c/path:/d/path',
                          LOADEDMODULES='a',
                          _LMFILES_=os.path.join(d1, 'a.py'))
        mc.unload('a')
        assert mc['envar1'] is None
        assert mc['envar2'] is None
        assert mc['path'] == '/a/path:/b/path'
        assert mc['key'] == '/c/path:/d/path'
        assert not mc[LM_KEY]
        assert not mc.modulepath.get_module_by_name('a').is_loaded

    @pytest.mark.sandbox
    def test_exec_unload_2(self):
        d1 = self.write_modules_a_b()
        modules = 'a:b'
        lm_files = ':'.join([os.path.join(d1, 'a.py'),
                             os.path.join(d1, 'b.py')])
        lm_refcnt = {'a': 1, 'b': 1}
        mc = tools.t_controller(modulepath=d1,
                          envar1='val1', envar2='val2',
                          path='/a/path:/b/path:/c/path:/d/path',
                          key='/c/path:/d/path',
                          LOADEDMODULES=modules,
                          _LMREFCNT_=dict2str(lm_refcnt),
                          _LMFILES_=lm_files)
        mc.unload('b')
        assert not mc.modulepath.get_module_by_name('b').is_loaded
        assert not mc.modulepath.get_module_by_name('a').is_loaded
        assert mc['envar1'] is None
        assert mc['envar2'] is None
        assert mc['path'] == '/a/path:/b/path'
        assert mc['key'] == '/c/path:/d/path'
        assert not mc[LM_KEY]

    @pytest.mark.unit
    def test_load_different_versions(self):

        mc = tools.t_controller(modulepath='')
        d1 = tools.t_make_temp_directory(self.datadir)
        name = 'a'
        d2 = os.path.join(d1, name)
        tools.t_make_directory(d2)

        assert mc.modulepath.get_module_by_name('a/1.0') is None
        assert mc.modulepath.get_module_by_name('a/2.0') is None

        # Write modulefiles
        with open(os.path.join(d2, '1.0.py'), 'w') as fh:
            fh.write('append_path("path", "/a1/path")')
        with open(os.path.join(d2, '2.0.py'), 'w') as fh:
            fh.write('prepend_path("path", "/a2/path")')

        # Modify MODULEPATH and `a` will become available
        mc.append_path(MP_KEY, d1)
        assert d1 in mc.environ[MP_KEY].split(os.pathsep)
        assert mc.modulepath.get_module_by_name('a') is not None

        # Load it
        mc.load('a/1.0')
        assert 'a/1.0' in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == '/a1/path'

        mc.load('a')
        assert 'a/2.0' in mc.environ.get_loaded_modules('names')
        assert 'a/1.0' not in mc.environ.get_loaded_modules('names')
        assert mc.environ['path'] == '/a2/path'

        assert mc.m_state_changed.get('VersionChanged') is not None
        mc.report_changed_module_state()

    @pytest.mark.sandbox
    def test_exec_load_do_not_register(self):
        d1 = self.write_modules_a_b(do_not_register=True)
        mc = tools.t_controller(modulepath=d1,
                          path='/a/path:/b/path',
                          key='/c/path:/d/path')
        a = mc.load('a')
        assert mc['envar1'] == 'val1'
        assert mc['envar2'] == 'val2'
        assert mc['path'] == '/a/path:/b/path:/c/path:/d/path'
        assert mc['key'] == '/c/path'
        assert LM_KEY not in mc
        assert not mc.modulepath.get_module_by_name('a').is_loaded
