import os
import pytest

import tools
from pymod.optparse import ModuleOptionParser


class TestModuleOptionParser(tools.TestBase):
    def test_option_parser_option_string(self):
        p = ModuleOptionParser()
        prefix_char = p.prefix_char
        try:
            p.add_option('{0}bar'.format(prefix_char))
        except:
            assert False, 'Parser should not have failed'
        try:
            p.add_option('bar')
            assert False, 'Parser should have failed because lacked prefix'
        except:
            pass
        try:
            p.add_option('{0}{0}bar'.format(prefix_char))
            assert False, 'Parser should have failed because double prefix'
        except:
            pass

    def test_option_parser_store_true(self):
        p = ModuleOptionParser()
        prefix_char = p.prefix_char
        option_string = '{0}baz'.format(prefix_char)
        p.add_option(option_string)
        option_string2 = '{0}spam'.format(prefix_char)
        p.add_option(option_string2, action='store')
        ns = p.parse_opts([])
        assert ns.baz is None
        ns = p.parse_opts([option_string])
        assert ns.baz is True
        s = p.description()
        try:
            p.parse_opts(['{0}=1'.format(option_string)])
            assert False, 'Parser should have failed because of explicit arg'
        except:
            pass
        bad_option_string = '{0}foo'.format(prefix_char)
        try:
            p.parse_opts(['{0}'.format(bad_option_string)])
            assert False, 'Parser should have failed because of invalid option'
        except:
            pass

    def test_option_parser_store_false(self):
        p = ModuleOptionParser()
        prefix_char = p.prefix_char
        option_string = '{0}baz'.format(prefix_char)
        p.add_option(option_string, action='store_false')
        ns = p.parse_opts([])
        assert ns.baz is None
        ns = p.parse_opts([option_string])
        assert ns.baz is False
        try:
            p.parse_opts(['{0}=1'.format(option_string)])
            assert False, 'Parser should have failed because of explicit arg'
        except:
            pass
        bad_option_string = '{0}foo'.format(prefix_char)
        try:
            p.parse_opts(['{0}'.format(bad_option_string)])
            assert False, 'Parser should have failed because of bad option'
        except:
            pass

    def test_option_parser_store(self):
        p = ModuleOptionParser()
        prefix_char = p.prefix_char
        option_string = '{0}baz'.format(prefix_char)
        p.add_option(option_string, action='store')
        ns = p.parse_opts([])
        assert ns.baz is None
        ns = p.parse_opts(['{0}=spam'.format(option_string)])
        assert ns.baz == 'spam'
        try:
            p.parse_opts(['{0}'.format(option_string)])
            assert False, 'Parser should have failed because lacked explicit arg'
        except:
            pass
        bad_option_string = '{0}foo'.format(prefix_char)
        try:
            p.parse_opts(['{0}=1'.format(bad_option_string)])
            assert False, 'Parser should have failed because of bad option'
        except:
            pass

    def test_option_parser_parse_bad_1(self):
        p = ModuleOptionParser()
        prefix_char = p.prefix_char
        o1 = '{0}baz'.format(prefix_char)
        p.add_option(o1)
        try:
            p.parse_opts(['baz'])
            assert False, 'Parser should not have failed because of bad option parsed'
        except:
            pass

    def test_option_parser_conflict_1(self):
        p = ModuleOptionParser()
        prefix_char = p.prefix_char
        o1 = '{0}baz'.format(prefix_char)
        o2 = '{0}spam'.format(prefix_char)
        p.add_mutually_exclusive_option(o1, o2)
        try:
            p.parse_opts([o1])
        except:
            assert False, 'Parser should not have failed because of conflicts'

    def test_option_parser_conflict_2(self):
        p = ModuleOptionParser()
        prefix_char = p.prefix_char
        o1 = '{0}baz'.format(prefix_char)
        o2 = '{0}spam'.format(prefix_char)
        p.add_mutually_exclusive_option(o1, o2)
        try:
            p.parse_opts([o1, o2])
            assert False, 'Parser should have failed because of conflicts'
        except:
            pass

    def test_option_parser_conflict_3(self):
        p = ModuleOptionParser()
        prefix_char = p.prefix_char
        o1 = '{0}baz'.format(prefix_char)
        o2 = 'spam'
        try:
            p.add_mutually_exclusive_option(o1, o2)
            assert False, 'Parser should have failed because of bad conflicts'
        except:
            pass

    def test_option_parser_bad_1(self):
        p = ModuleOptionParser()
        prefix_char = p.prefix_char
        try:
            p.add_option('+foo', action='bad_action')
            assert False, 'Parser should have failed because of bad action'
        except:
            pass

    def test_option_parser_bad_2(self):
        p = ModuleOptionParser()
        prefix_char = p.prefix_char
        p.add_option('{0}foo'.format(prefix_char))
        try:
            p.add_option('{0}foo'.format(prefix_char))
            assert False, 'Parser should have failed because of duplicate'
        except:
            pass

