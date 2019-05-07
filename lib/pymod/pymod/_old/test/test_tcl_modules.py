import os
import pytest

import tools
from pymod.modulepath import Modulepath
from pymod.tcl2py import tcl2py

@pytest.mark.skipif(tools.t_no_tcl, reason='No TCL modulecmd')
class TestTCLModules(tools.TestBase):


    def write_module_in_dirname(self, dirname, contents, name='module'):
        f = os.path.join(dirname, name)
        with open(f, 'w') as fh:
            fh.write("#%Module1.0{0}\n".format("#"*69))
            fh.write(contents)
        return os.path.basename(f)

    @pytest.mark.unit
    def test_tcl_default_version(self):
        d1 = tools.t_make_temp_directory(self.datadir)
        d2 = tools.t_make_temp_directory(d1)
        pkg = os.path.basename(d2)
        m1 = os.path.join(pkg, '1.0')
        m2 = os.path.join(pkg, '2.0')
        self.write_module_in_dirname(d1, "append-path path  /b/path", 'a')
        self.write_module_in_dirname(d2, "setenv envar1 1.0", "1.0")
        self.write_module_in_dirname(d2, "setenv envar1 2.0", "2.0")
        c = 'set ModulesVersion "1.0"'
        self.write_module_in_dirname(d2, c, ".version")
        mp = Modulepath([d1])
        assert mp.get_module_by_name('a').name == 'a'
        assert mp.get_module_by_name(pkg).fullname == m1
        assert mp.get_module_by_name(m1).is_default
        assert mp.get_module_by_name(m2).fullname == m2
        assert not mp.get_module_by_name(m2).is_default

    @pytest.mark.unit
    def test_tcl_default(self):
        d1 = tools.t_make_temp_directory(self.datadir)
        d2 = tools.t_make_temp_directory(d1)
        pkg = os.path.basename(d2)
        m1 = os.path.join(pkg, '1.0')
        m2 = os.path.join(pkg, '2.0')
        self.write_module_in_dirname(d1, "append-path path  /b/path", 'a')
        self.write_module_in_dirname(d2, "setenv envar1 1.0", "1.0")
        self.write_module_in_dirname(d2, "setenv envar1 2.0", "2.0")
        mp = Modulepath([d1])
        assert mp.get_module_by_name('a').name == 'a'
        assert mp.get_module_by_name(m1).fullname == m1
        assert mp.get_module_by_name(m2).is_default
        assert mp.get_module_by_name(pkg).fullname == m2
        assert not mp.get_module_by_name(m1).is_default

    tcl_basic_module = """\
proc ModulesHelp { } {
        global dotversion

        puts stderr "\tAdds `.' to your PATH environment variable"
        puts stderr "\n\tThis makes it easy to add the current working directory"
        puts stderr "\tto your PATH environment variable.  This allows you to"
        puts stderr "\trun executables in your current working directory"
        puts stderr "\twithout prepending ./ to the excutable name"
        puts stderr "\n\tVersion $dotversion\n"
}

module-whatis   "adds `.' to your PATH environment variable"

# for Tcl script use only
set     dotversion      3.2.10

append-path     path /b/path
prepend-path    path /a/path
setenv foo BAR
set-alias alias BAZ
"""

    @pytest.mark.tcl
    @pytest.mark.sandbox
    def test_tcl_basic_load(self):
        d1 = tools.t_make_temp_directory(self.datadir)
        self.write_module_in_dirname(d1, self.tcl_basic_module, 'a')
        mc = tools.t_controller(modulepath=d1)
        mc.load('a')
        assert mc['path'] == '/a/path:/b/path'
        assert mc['foo'] == 'BAR'
        assert 'alias' in mc.aliases or 'alias' in mc.shell_functions
        if 'alias' in mc.aliases:
            assert mc.aliases['alias'] == 'BAZ'
        else:
            assert mc.shell_functions['alias'] == 'BAZ'
        mc.show('a')

    @pytest.mark.tcl
    def test_tcl_basic_avail(self):
        d1 = tools.t_make_temp_directory(self.datadir)
        self.write_module_in_dirname(d1, self.tcl_basic_module, 'a')
        mp = Modulepath([d1])
        m = mp.get_module_by_name('a')
        assert m.type == 'TCL'
