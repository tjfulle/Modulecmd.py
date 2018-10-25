import os
import pytest

import tools


class TestPrerequisite(tools.TestBase):

    def write_modules(self):
        d1 = tools.t_make_temp_directory(self.datadir)
        with open(os.path.join(d1, 'a.py'), 'w') as fh:
            fh.write("append_path('path', '/a/path')")
        with open(os.path.join(d1, 'b.py'), 'w') as fh:
            fh.write("append_path('path', '/b/path')")
        with open(os.path.join(d1, 'c.py'), 'w') as fh:
            fh.write("prereq('a', 'b')")
        with open(os.path.join(d1, 'd.py'), 'w') as fh:
            fh.write("prereq_any('a', 'b')")
        with open(os.path.join(d1, 'e.py'), 'w') as fh:
            fh.write("conflict('f')")
        with open(os.path.join(d1, 'f.py'), 'w') as fh:
            fh.write("")
        return d1

    @pytest.mark.sandbox
    def test_has_prereq(self):
        d1 = self.write_modules()
        mc = tools.t_controller(modulepath=d1)
        mc.load('a')
        mc.load('b')
        mc.prereq('b', 'a')

    @pytest.mark.sandbox
    def test_has_prereq_any(self):
        d1 = self.write_modules()
        mc = tools.t_controller(modulepath=d1)
        mc.load('a')
        mc.load('b')
        mc.prereq_any('b', 'a')

    @pytest.mark.sandbox
    def test_missing_prereq1(self):
        d1 = self.write_modules()
        mc = tools.t_controller(modulepath=d1)
        mc.load('a')
        try:
            mc.prereq('b', 'a')
            raise Exception('Error not caught')
        except:
            pass

    @pytest.mark.sandbox
    def test_missing_prereq2(self):
        d1 = self.write_modules()
        mc = tools.t_controller(modulepath=d1)
        mc.load('b')
        try:
            mc.prereq('a', 'b')
            raise Exception('Error not caught')
        except:
            pass

    @pytest.mark.sandbox
    def test_exec_has_prereq(self):
        d1 = self.write_modules()
        mc = tools.t_controller(modulepath=d1)
        mc.load('a')
        mc.load('b')
        mc.load('c')

    @pytest.mark.sandbox
    def test_exec_has_prereq_any_1(self):
        d1 = self.write_modules()
        mc = tools.t_controller(modulepath=d1)
        mc.load('a')
        mc.load('d')

    @pytest.mark.sandbox
    def test_exec_has_prereq_any_2(self):
        d1 = self.write_modules()
        mc = tools.t_controller(modulepath=d1)
        mc.load('b')
        mc.load('d')

    @pytest.mark.sandbox
    def test_exec_missing_prereq_any(self):
        d1 = self.write_modules()
        mc = tools.t_controller(modulepath=d1)
        try:
            mc.load('d')
            raise Exception('Error not caught')
        except:
            pass

    @pytest.mark.sandbox
    def test_exec_missing_prereq1(self):
        d1 = self.write_modules()
        mc = tools.t_controller(modulepath=d1)
        mc.load('a')
        try:
            mc.load('c')
            raise Exception('Error not caught')
        except:
            pass

    @pytest.mark.sandbox
    def test_exec_missing_prereq2(self):
        d1 = self.write_modules()
        mc = tools.t_controller(modulepath=d1)
        mc.load('b')
        try:
            mc.load('c')
            raise Exception('Error not caught')
        except:
            pass

    @pytest.mark.sandbox
    def test_exec_conflict(self):
        d1 = self.write_modules()
        mc = tools.t_controller(modulepath=d1)
        mc.load('e')
        mc.load('f')
        mc.unload('f')
        mc.unload('e')
        mc.load('f')
        try:
            mc.load('e')
            raise Exception('Conflict not caught')
        except:
            pass

