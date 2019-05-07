import pytest

import tools


class TestPrependPath(tools.TestBase):

    @pytest.mark.unit
    def test_prepend_path_set(self):
        mc = tools.t_controller(modulepath='')
        mc.prepend_path('path', '/a/path')
        assert mc['path'] == '/a/path'

    @pytest.mark.unit
    def test_prepend_path(self):
        mc = tools.t_controller(modulepath='', path='/b/path')
        mc.prepend_path('path', '/a/path')
        assert mc['path'] == '/a/path:/b/path'

    @pytest.mark.unit
    def test_prepend_path_list_load_mode(self):
        mc = tools.t_controller(modulepath='', path='/c/path')
        mc.prepend_path('path', '/a/path', '/b/path')
        assert mc['path'] == '/a/path:/b/path:/c/path'
