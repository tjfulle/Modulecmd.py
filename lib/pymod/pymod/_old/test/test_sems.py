import os
import pytest


import tools

no_sems = not os.path.isdir('/projects/sems')
@pytest.mark.skipif(True, reason='SEMS not compatible with new TCL converter')
class TestSemsTCL(tools.TestBase):


    def write_module(self):
        d1 = tools.t_make_temp_directory(self.datadir)
        with open(os.path.join(d1, 'a.py'), 'w') as fh:
            fh.write("""\
prefix = '/projects/sems/modulefiles'
if os.path.isdir(prefix):
    if system_is_darwin():
        platform = 'Darwin10.11-x86_64'
    else:
        platform = 'rhel6-x86_64'
    setenv('SEMS_MODULEFILES_ROOT', prefix)
    prepend_path('MODULEPATH', os.path.join(prefix, 'projects'))
    prepend_path('MODULEPATH', os.path.join(prefix, platform, 'sems/utility'))
    prepend_path('MODULEPATH', os.path.join(prefix, platform, 'sems/tpl'))
    prepend_path('MODULEPATH', os.path.join(prefix, platform, 'sems/compiler'))
""")
        return d1

    @pytest.mark.tcl
    @pytest.mark.sandbox
    @pytest.mark.skipif(tools.t_no_tcl, reason='No TCL')
    @pytest.mark.skipif(no_sems, reason='No SEMS')
    def test_sems_tcl(self):
        d1 = self.write_module()
        environ = dict(os.environ)
        environ[LM_FILES_KEY] = ''
        environ[LM_KEY] = ''
        environ[MP_KEY] = d1
        mc = tools.t_controller(modulepath=d1, _LMFILES_='', LOADEDMODULES='')
        mc.load('a')
        mc.load('sems-gcc')
        assert mc.get('SEMS_COMPILER_NAME') == 'gcc'
        mc.load('sems-openmpi')
        assert mc.get('SEMS_MPI_NAME') == 'openmpi'
        mc.load('sems-boost/1.58.0/base')
        mc.unload('sems-gcc')
        assert mc.get('SEMS_COMPILER_NAME') is None

