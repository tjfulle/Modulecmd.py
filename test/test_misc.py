import os
import sys
import pytest

import tools
from pymod.utils import *
from pymod.compat import *
from pymod.defaults import MP_KEY

class TestMisc(tools.TestBase):
    def test_join(self):
        assert join(['a', 'b'], '#') == 'a#b'
    def test_split(self):
        assert tuple(split('a#b', sep='#')) == ('a', 'b')
        assert tuple(split('a  b')) == ('a', 'b')
    def test_has_tclsh(self):
        # Just test that it runs without failing
        tools.t_has_tclsh()
    def test_strip_quotes(self):
        string = '"a"'
        assert strip_quotes(string) == 'a'
        string = "'b'"
        assert strip_quotes(string) == 'b'
    def test_listdir(self):
        d = os.path.dirname(os.path.realpath(__file__))
        this_file = os.path.basename(__file__)
        assert this_file in listdir(d)
        assert this_file not in listdir(d, key=lambda x: x!=__file__)
        d = '/spam/baz/foo'
        assert listdir(d) is None
    def test_which(self):
        the_python = sys.executable
        python = which('python', PATH=os.path.dirname(the_python))
        assert python == the_python
        baz = which('baz', default='bar')
        assert baz == 'bar'
        python = which('python')
        assert python is not None
        ls = which('/bin/ls')
        assert ls is not None
    def is_executable(self):
        assert is_executable(sys.executable)
        assert not is_executable('/usr/bin/baz-spam')
    def test_lists_are_same(self):
        l1 = [1, 'a', 5.]
        t1 = (1, 'a', 5.)
        assert lists_are_same(l1, t1)
        l2 = [1, 'a', None, 4]
        assert not lists_are_same(l1, l2)
        l3 = [1, 'a', None]
        assert not lists_are_same(l1, l3)
        assert lists_are_same(l1, l3, lambda x: 5. if x is None else x)
    def test_wrap2(self):
        a = ['a', 'b', 'c', 'd', 'e', 'f']
        s = wrap2(a, 30)
        assert s == '   a   b   c   d   e   f'
        s = wrap2(a, 30, pad=' ')
        assert s == ' a b c d e f'
        s = wrap2(a, 14)
        assert s == '   a   c   e\n   b   d   f'
        assert wrap2('', 10) == ''
    def test_get_console_dims(self):
        # just see if it runs
        get_console_dims()
        get_console_dims(default_rows=5)
        get_console_dims(default_rows=5, default_cols=5)
    def test_check_output(self):
        d = os.path.dirname(os.path.realpath(__file__))
        command = ['ls', d+os.path.sep]
        cwd = os.getcwd()
        os.chdir(d)
        out = [x for y in check_output(command).split('\n')
               for x in y.split(' ') if x.split()]
        os.chdir(cwd)
        assert os.path.basename(__file__) in out
    def test_decode_str(self):
        # just see if it runs
        s = decode_str("a string")
        assert isinstance(s, string_types)
        assert decode_str(None) is None
    def test_join_args(self):
        assert join_args('a', 'b', 'c', None, 5., 4) == 'a b c None 5.0 4'
    def test_total_module_time(self):
        import time
        t0 = time.time()
        t = total_module_time(time.time())
        tf = time.time()
    def test_import_module_by_filepath(self):
        filename = os.path.join(self.datadir, 'baz.py')
        with open(filename, 'w') as fh:
            fh.write('spam = 1\n')
        baz = import_module_by_filepath(filename)
        os.remove(filename)
        assert baz.spam == 1
        if 'baz' in sys.modules:
            del sys.modules['baz']
    def test_wrong_type_module_exception(self):
        def fun(name):
            raise WrongTypeModule(name)
        try:
            fun('a')
        except:
            pass
    @pytest.mark.unit
    def test_empty_dump(self):
        mc = tools.t_controller(modulepath='')
        mc.dump()
    @pytest.mark.unit
    def test_dump_2(self):
        mc = tools.t_controller(modulepath='')
        mc.environ['FOOBAR'] = 'BAZ'
        s = mc.dump()
        assert s.strip() ==  'FOOBAR="BAZ";\nexport FOOBAR;'
        dryrun = True
        mc.dump(stream=sys.stderr)
    def test_str2dict(self):
        d = {'spam': 'baz'}
        s = dict2str(d)
        dikt = str2dict(s)
        assert dikt == d


class TestControllerMisc(tools.TestBase):
    def write_modules(self, n):
        for i in range(n):
            filename = os.path.join(self.datadir, 'f{0}.py'.format(i+1))
            with open(filename, 'w') as fh:
                fh.write("setenv('ENVAR_{0}', '{0}')\n".format(i+1))
    def remove_modules(self):
        for filename in glob.glob(os.path.join(self.datadir, '*.py')):
            os.remove(filename)
    def test_get_loaded_modules(self):
        self.write_modules(2)
        mc = tools.t_controller(modulepath=self.datadir)
        mc.load("f1")
        mc.load("f2")
        for (i,m) in enumerate(mc.get_loaded_modules(), start=1):
            assert m.name == "f{0}".format(i)
        # loaded_modules is just a wrapper to get_loaded_modules
        for (i,m) in enumerate(mc.get_loaded_modules(reverse=1)):
            j = 2 - i
            assert m.name == "f{0}".format(j)
        lm = mc.get_loaded_modules(key=lambda x: x.name=="f1")
        assert len(lm) == 1
        assert lm[0].name == 'f1'

        os.remove(os.path.join(self.datadir, 'f1.py'))
        try:
            mc.get_loaded_modules()
            assert False, "should have thrown"
        except:
            pass
    def test_load_by_filename(self):
        self.write_modules(1)
        mc = tools.t_controller(modulepath='')
        filename = os.path.join(self.datadir, 'f1.py')
        assert os.path.isfile(filename)
        mc.load(filename)
        assert mc[MP_KEY] == self.datadir
        lm = mc.get_loaded_modules()
        assert len(lm) == 1
        os.remove(os.path.join(self.datadir, 'f1.py'))

