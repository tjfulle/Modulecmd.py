import os
import pytest

import tools
from pymod.modulepath import Modulepath
from pymod.tcl2py import tcl2py

@pytest.mark.skipif(tools.t_no_tcl, reason='No TCL modulecmd')
class TestTCLModules(tools.TestBase):

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

    def write_module_in_dirname(self, dirname, contents, name='module'):
        f = os.path.join(dirname, name)
        with open(f, 'w') as fh:
            fh.write("#%Module1.0{0}\n".format("#"*69))
            fh.write(contents)
        return os.path.basename(f)

    @pytest.mark.tcl
    def test_tcl2py_1(self):
        d1 = tools.t_make_temp_directory(self.datadir)
        self.write_module_in_dirname(d1, self.tcl_basic_module, 'gcc')
        mc = tools.t_controller(modulepath=d1, DYLD_LIBRARY_PATH='path_a',
                                LD_LIBRARY_PATH='path_b', LD_PRELOAD='path_c')
        m = mc.get_module('gcc')
        assert m.type == 'TCL'
        stdout = tcl2py(m, 'load', mc.environ)

    @pytest.mark.tcl
    def test_tcl2py_2(self):
        d1 = tools.t_make_temp_directory(self.datadir)
        self.write_module_in_dirname(d1, self.tcl_basic_module, 'openmpi')
        mc = tools.t_controller(modulepath=d1, DYLD_LIBRARY_PATH='path_a',
                                LD_LIBRARY_PATH='path_b', LD_PRELOAD='path_c')
        m = mc.get_module('openmpi')
        assert m.type == 'TCL'
        stdout = tcl2py(m, 'load', mc.environ)

    @pytest.mark.tcl
    def test_tcl2py_3(self):
        d1 = tools.t_make_temp_directory(self.datadir)
        self.write_module_in_dirname(d1, self.tcl_basic_module, 'python')
        mc = tools.t_controller(modulepath=d1, DYLD_LIBRARY_PATH='path_a',
                                LD_LIBRARY_PATH='path_b', LD_PRELOAD='path_c')
        m = mc.get_module('python')
        assert m.type == 'TCL'
        stdout = tcl2py(m, 'load', mc.environ)
