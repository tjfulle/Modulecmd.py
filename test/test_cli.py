import os
import pytest

import tools
import pymod
from pymod.defaults import MP_KEY, LM_KEY, LM_FILES_KEY, LM_OPTS_KEY, DEFAULT_USER_COLLECTION_NAME
from pymod.compat import import_module_by_filepath
from pymod.utils import dict2str


class TestCommandLineInterface(tools.TestBase):

    def setup_class(self):

        self.datadir = tools.t_make_temp_directory()
        self.dotdir = os.path.join(self.datadir, 'pymod.d')
        tools.t_make_directory(self.dotdir)

        self.modulepath = os.path.join(self.datadir, 'modules')

        self.old = {}
        self.old[MP_KEY] = os.environ.pop(MP_KEY, None)
        self.old[LM_KEY] = os.environ.pop(LM_KEY, None)
        self.old['VAR_0'] = None

        os.environ['PYMOD_DOT_DIR'] = self.dotdir
        os.environ[MP_KEY] = self.modulepath
        os.environ[LM_KEY] = 'f0'
        os.environ[LM_FILES_KEY] = os.path.join(self.modulepath, 'f0.py')
        os.environ[LM_OPTS_KEY] = dict2str({"f0": None})
        os.environ['VAR_0'] = 'VAL_0'

        tools.t_make_directory(self.modulepath)

        pymod.user._dot_dir(reset=1)

        for i in (0, 1, 2):
            with open(os.path.join(self.modulepath, 'f{0}.py'.format(i)), 'w') as fh:
                key, val = 'VAR_{0}'.format(i), 'VAL_{0}'.format(i)
                fh.write("add_option('+x')\n")
                fh.write('setenv({0!r}, {1!r})\n'.format(key, val))

    def teardown_class(self):
        for (key, val) in self.old.items():
            os.environ.pop(key, None)
            if val is not None:
                os.environ[key] = val
        tools.t_remove_directory(self.modulepath)
        tools.t_remove_directory(self.datadir)

    def main(self, argv):
        x = pymod.main(argv)
        return x

    def set_default_os_environ(self):
        os.environ[MP_KEY] = self.modulepath
        os.environ[LM_KEY] = 'f0'
        os.environ[LM_FILES_KEY] = os.path.join(self.modulepath, 'f0.py')
        os.environ[LM_OPTS_KEY] = dict2str({"f0": None})
        os.environ['VAR_0'] = 'VAL_0'

    @pytest.mark.skipif(True, reason='capsys not working')
    def test_avail(self, capsys):
        capsys.readouterr()
        self.main(['bash', 'avail'])
        out, err = capsys.readouterr()
        err = [x.strip() for x in err.split('\n')[1].split() if x.split()]
        assert err[0] == 'f0'
        # err[1] is some color code
        assert err[2] == 'f1'
        assert err[3] == 'f2'

        self.main(['bash', 'avail', '--terse'])
        out, err = capsys.readouterr()
        err = err.split('\n')
        assert err[0].split(':')[0].strip() == self.modulepath
        assert err[1] == 'f0'
        assert err[2] == 'f1'
        assert err[3] == 'f2'

    def test_show(self, capsys):
        self.main(['bash', 'show', 'f1'])
        out, err = capsys.readouterr()
        assert err.split('\n')[-2] == "setenv('VAR_1', 'VAL_1')"
        capsys.readouterr()
        self.main(['bash', 'show', 'f1'])
        out, err = capsys.readouterr()
        assert err.split('\n')[-2] == "setenv('VAR_1', 'VAL_1')"

    def test_file(self, capsys):
        self.main(['bash', 'file', 'f1'])
        out, err = capsys.readouterr()
        assert err.strip() == os.path.join(self.modulepath, 'f1.py')

    def test_list(self, capsys):
        self.main(['bash', 'list'])
        out, err = capsys.readouterr()
        err = [x.strip() for x in err.split('\n') if x.split()]
        assert err[0] == 'Currently loaded modules:'
        assert err[1] == '1) f0'
        assert len(err) == 2

        self.main(['bash', 'list', '--terse'])
        self.main(['bash', 'list', 'f0', '--terse'])

    def test_whatis(self, capsys):
        self.main(['bash', 'whatis', 'f1'])

    @pytest.mark.skipif(True, reason='capsys not working')
    def test_collection(self, capsys):
        name = DEFAULT_USER_COLLECTION_NAME
        self.main(['bash', 'save'])
        filename = os.path.join(self.dotdir, 'collections.json')
        assert os.path.isfile(filename)

        name = 'test'
        os.environ[LM_KEY] = 'f0:f1'
        os.environ[LM_FILES_KEY] = os.path.join(self.modulepath,'f0.py')+':'+ \
                                  os.path.join(self.modulepath,'f1.py')
        os.environ[LM_OPTS_KEY] = dict2str({"f": None, "f1": None})
        self.main(['bash', 'save', name])

        self.main(['bash', 'savelist'])
        out, err = capsys.readouterr()
        s = ' '.join(err.split('\n')[0].split())
        #assert s == name

        os.environ[LM_KEY] = ''
        os.environ[LM_FILES_KEY] = ''
        os.environ[LM_OPTS_KEY] = ''
        os.environ.pop('VAR_0')

        self.main(['bash', 'restore', name])
        out, err = capsys.readouterr()
        for line in out.split('\n'):
            if line.startswith(LM_KEY):
                assert line.split('=')[1] == '"f0:f1";'

        self.main(['bash', 'restore'])
        out, err = capsys.readouterr()
        for line in out.split('\n'):
            if line.startswith(LM_KEY):
                assert line.split('=')[1] == '"f0";'

        # savelist
        self.main(['bash', 'savelist'])
        out, err = capsys.readouterr()
        s = [' '.join(x.split()) for x in err.split('\n') if x.split()]
        assert s[0] == name

        # savelist
        self.main(['bash', 'savelist', '--terse'])
        out, err = capsys.readouterr()
        err = [x.strip() for x in err.split('\n') if x.split()]
        assert err[0] == name

        # describe
        self.main(['bash', 'describe', name])
        out, err = capsys.readouterr()
        err = [x.strip() for x in err.split('\n') if x.split()]
        assert err[0] == 'use({0!r})'.format(self.modulepath)
        assert err[1] == "load('f0')"
        assert err[2] == "load('f1')"

        self.main(['bash', 'saverm', name])

        self.set_default_os_environ()

    def test_setenv(self, capsys):
        self.main(['bash', 'shell', 'env', 'foo=bar'])
        out, err = capsys.readouterr()
        out = [x.strip() for x in out.split('\n') if x.split()]
        for line in out:
            if line.startswith('_CLSETENV_='):
                assert line.split('=')[1].strip() == '"foo";'
            elif line.startswith('foo='):
                assert line.split('=')[1].strip() == '"bar";'

    def test_load(self, capsys):
        self.main(['bash', 'load', 'f1'])
        out, err = capsys.readouterr()
        for line in out:
            if line.startswith('VAR_1='):
                assert line.split('=')[1].strip() == '"VAL_1";'

    def test_reload(self, capsys):
        self.main(['bash', 'reload', 'f0'])
        out, err = capsys.readouterr()
        for line in out:
            if line.startswith('VAR_0='):
                assert line.split('=')[1].strip() == '"VAL_0";'

    def test_reload(self, capsys):
        self.main(['bash', 'unload', 'f0'])

    def test_refresh(self, capsys):
        self.main(['bash', 'refresh'])

    def test_swap(self, capsys):
        self.main(['bash', 'swap', 'f0', 'f1'])

    def test_purge(self, capsys):
        self.main(['bash', 'purge'])

    def test_use(self, capsys):
        d = os.path.join(self.datadir, 'foo')
        tools.t_make_directory(d)
        self.main(['bash', 'use', d])

    def test_unuse(self, capsys):
        self.main(['bash', 'unuse', self.modulepath])

    def test_cl_help(self, capsys):
        try:
            self.main(['bash', '--help'])
            assert False
        except:
            pass
        out, err = capsys.readouterr()
        try:
            self.main(['bash', '-h'])
            assert False
        except:
            pass
        out, err = capsys.readouterr()

    def test_options(self):
        self.main(['bash', 'load', 'f1', '+x'])
        try:
            self.main(['bash', 'load', '+x' 'f1'])
            assert False
        except:
            pass
        try:
            self.main(['bash', 'load', 'f1', '+x-'])
            assert False
        except:
            pass

    def test_cl_reload(self):
        self.main(['bash', 'reload', 'f1'])

