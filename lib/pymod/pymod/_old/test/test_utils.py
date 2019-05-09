import tools
import pymod.utils as ut

class TestUtils(tools.TestBase):

    def test_split(self):
        s = "a:b:c:d"
        x = ut.split(s, sep=':')
        assert ut.lists_are_same(['a', 'b', 'c', 'd'], x)
        x = ut.split(s, num=1, sep=':')
        assert ut.lists_are_same(['a', 'b:c:d'], x)

    def test_join(self):
        assert 'a;b;c' == ut.join(('a', 'b', 'c'), sep=';')

    def test_join_args(self):
        args = ['a', 1, {'x': '1'}, 'd']
        x = ut.join_args(*args)
        assert x == "a 1 {'x': '1'} d"

    def test_decode_str(self):
        assert ut.decode_str(None) is None
        assert ut.decode_str(u'abcd') == 'abcd'

    def test_encode_str(self):
        assert ut.encode_str('abcd') == b'abcd'

    def test_check_output(self):
        files = ut.check_output('ls')

    def test_get_console_dims(self):
        rows, columns = ut.get_console_dims()

    def test_dict2str(self):
        d = {'a': 'b', 'c': 1}
        s = ut.dict2str(d)
        assert ut.str2dict(s) == d

    def test_total_module_time(self):
        t = ut.total_module_time(0.)

    def test_lists_are_same(self):
        assert not ut.lists_are_same([1], [1,2])
        assert not ut.lists_are_same([1,3], [1,2])
        assert ut.lists_are_same([1,2], [1,2])
        assert ut.lists_are_same([1,2], [1,2], key=lambda x: 2*x)


    def test_grep_pat_in_string(self):
        s = ut.grep_pat_in_string('A\nString', 'foo')
        assert s == 'A\nString'
        s = ut.grep_pat_in_string('This is\nthe string', 'string')
        x = s.split('\n')
        assert x[0] == 'This is'
        assert not x[1] == 'the string'

    def test_wrap2(self):
        ut.wrap2(None, 10)
        x = [x for x in 'abcdefghijklmnopqrstuvwxyz']
        s = ut.wrap2(x, 4)
        assert ut.lists_are_same(x, [_.strip() for _ in s.split('\n')])

    def test_get_unique(self):
        x = [1, 2, 3, 4, 3, 4, 5, 6, 2]
        u, e = ut.get_unique(x)
        assert ut.lists_are_same(u, [1, 2, 3, 4, 5, 6])
        assert ut.lists_are_same(e, [3, 4, 2])

    def test_is_executable(self):
        assert not ut.is_executable('foobar-baz')
        assert ut.is_executable('/usr/bin/less')

    def test_which(self):
        assert ut.which('less') == '/usr/bin/less'
        assert ut.which('foobar-baz') is None

    def test_listdir(self):
        assert ut.listdir('/baz/bar') is None
        ut.listdir('/usr/bin')
        ut.listdir('/usr/bin')
        ut.listdir('/usr/bin', key=lambda x: True)

    def test_strip_quotes(self):
        s = '"a string"'
        assert ut.strip_quotes('"a string"') == 'a string'

    def test_textfill(self):
        ut.textfill('my string', width=4, indent=2)
