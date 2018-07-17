import os
import pytest

import tools


class TestRemovePath(tools.TestBase):


    def write_module(self, sep=None, uselist=False):
        d1 = tools.t_make_temp_directory(self.datadir)
        args = ["'path'", "'/b/path'"]
        if uselist:
            args.append("'/c/path'")
        if sep:
            args.append("sep='{0}'".format(sep))
        with open(os.path.join(d1, 'a.py'), 'w') as fh:
            fh.write("remove_path({0})".format(', '.join(args)))
        return d1

    @pytest.mark.unit
    def test_remove_path(self):
        mc = tools.t_controller(modulepath='', path='/a/path:/b/path')
        mc.remove_path('path', '/b/path')
        assert mc['path'] == '/a/path'

    @pytest.mark.unit
    def test_mf_remove_path_nondefault_sep(self):
        mc = tools.t_controller(modulepath='', path='/a/path;/b/path')
        mc.remove_path('path', '/b/path', sep=';')
        assert mc['path'] == '/a/path'

    @pytest.mark.unit
    def test_mf_remove_path_list(self):
        mc = tools.t_controller(modulepath='', path='/a/path:/b/path:/c/path')
        mc.remove_path('path', '/b/path', '/c/path')
        assert mc['path'] == '/a/path'

    @pytest.mark.unit
    def test_mf_remove_path_remove(self):
        mc = tools.t_controller(modulepath='', path='/a/path')
        mc.remove_path('path', '/a/path')
        assert mc['path'] is None

    @pytest.mark.sandbox
    def test_exec_remove_path_load_mode(self):
        d1 = self.write_module()
        mc = tools.t_controller(modulepath=d1, path='/a/path:/b/path')
        mc.load('a')
        assert mc['path'] == '/a/path'

    @pytest.mark.sandbox
    def test_exec_remove_path_unload_mode(self):
        d1 = self.write_module()
        mc = tools.t_controller(modulepath=d1, path='/a/path:/b/path')
        mc.unload('a')
        assert mc['path'] == '/a/path:/b/path'

    @pytest.mark.sandbox
    def test_exec_remove_path_load_mode_nondefault_sep(self):
        d1 = self.write_module(sep=';')
        mc = tools.t_controller(modulepath=d1, path='/a/path;/b/path')
        mc.load('a')
        assert mc['path'] == '/a/path'

    @pytest.mark.sandbox
    def test_exec_remove_path_unload_mode_nondefault_sep(self):
        d1 = self.write_module(sep=';')
        mc = tools.t_controller(modulepath=d1, path='/a/path;/b/path')
        mc.unload('a')
        assert mc['path'] == '/a/path;/b/path'

    @pytest.mark.sandbox
    def test_exec_remove_path_list_load_mode(self):
        d1 = self.write_module(uselist=True)
        mc = tools.t_controller(modulepath=d1, path='/a/path:/b/path:/c/path')
        mc.load('a')
        assert mc.get('path') == '/a/path'

    @pytest.mark.sandbox
    def test_exec_remove_path_list_unload_mode(self):
        d1 = self.write_module(uselist=True)
        mc = tools.t_controller(modulepath=d1, path='/a/path:/b/path:/c/path')
        mc.unload('a')
        assert mc.get('path') == '/a/path:/b/path:/c/path'

    @pytest.mark.sandbox
    def test_exec_remove_path_unload_mode_remove(self):
        d1 = self.write_module()
        mc = tools.t_controller(modulepath=d1, path='/b/path')
        mc.load('a')
        assert mc.get('path') is None

