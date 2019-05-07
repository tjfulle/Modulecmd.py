import os
import pytest

import tools


class TestAppendPath(tools.TestBase):

    @pytest.mark.unit
    def test_append_path_set(self):
        mc = tools.t_controller(modulepath='')
        mc.append_path('path', '/a/path')
        assert mc.environ['path'] == '/a/path'

    @pytest.mark.unit
    def test_append_path(self):
        mc = tools.t_controller(modulepath='', path='/a/path')
        mc.append_path('path', '/b/path')
        assert mc.environ['path'] == '/a/path:/b/path'

    @pytest.mark.unit
    def test_append_path_list(self):
        mc = tools.t_controller(modulepath='', path='/a/path')
        mc.append_path('path', '/b/path', '/c/path')
        assert mc.environ['path'] == '/a/path:/b/path:/c/path'

    @pytest.mark.unit
    def test_mf_append_path_nondefault_sep(self):
        mc = tools.t_controller(modulepath='', path='/a/path')
        mc.append_path('path', '/b/path', sep=';')
        assert mc.environ['path'] == '/a/path;/b/path'
        mc = tools.t_controller(modulepath='', path='/a/path')
        mc.append_path('path', '/b/path', sep=';')
        assert mc.environ['path'] == '/a/path;/b/path'

    @pytest.mark.sandbox
    def test_exec_append_path1(self):
        d = tools.t_make_temp_directory(self.datadir)
        with open(os.path.join(d, 'f.py'), 'w') as fh:
            fh.write("""
assert os.path.basename(self.filename) == 'f.py'
append_path('path', '/b/path')""")
        mc = tools.t_controller(modulepath=d)
        mc.load('f')
        assert mc['path'] == '/b/path'

    @pytest.mark.sandbox
    def test_exec_append_path2(self):
        d = tools.t_make_temp_directory(self.datadir)
        with open(os.path.join(d, 'f.py'), 'w') as fh:
            fh.write("""
assert os.path.basename(self.filename) == 'f.py'
append_path('path', '/b/path')""")
        mc = tools.t_controller(modulepath=d, path='/a/path')
        mc.load('f')
        assert mc['path'] == '/a/path:/b/path'
        mc.unload('f')
        assert mc['path'] == '/a/path'

    @pytest.mark.sandbox
    def test_exec_append_path3(self):
        d = tools.t_make_temp_directory(self.datadir)
        with open(os.path.join(d, 'f.py'), 'w') as fh:
            fh.write("""
assert os.path.basename(self.filename) == 'f.py'
append_path('path', '/b/path')""")
        mc = tools.t_controller(modulepath=d)
        mc.load('f')
        assert mc['path'] == '/b/path'
        mc.unload('f')
        assert mc['path'] is None

    @pytest.mark.sandbox
    def test_exec_append_path_list1(self):
        d = tools.t_make_temp_directory(self.datadir)
        with open(os.path.join(d, 'f.py'), 'w') as fh:
            fh.write("""
assert os.path.basename(self.filename) == 'f.py'
append_path('path', '/b/path', '/c/path')""")
        mc = tools.t_controller(modulepath=d, path='/a/path')
        mc.load('f')
        assert mc['path'] == '/a/path:/b/path:/c/path'
        mc.unload('f')
        assert mc['path'] == '/a/path'
