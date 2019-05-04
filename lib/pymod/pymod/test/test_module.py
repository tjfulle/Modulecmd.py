import os
import pytest
from pymod.module.version import Version
from pymod.module.option import ModuleOptionParser, ModuleArgumentParser


class TestModuleVersion:
    def test_version_major(self):
        v = Version('2')
        assert v.major == 2
        assert v.minor == v.patch == v.micro == None
        assert v < Version('4.0.0')
        assert v < Version('2.3.9')
        assert v > Version('1.0.0')
        assert v == Version('2')

    def test_version_major_minor(self):
        v = Version('2.1')
        assert v.major == 2
        assert v.minor == 1
        assert v.patch == v.micro == None
        assert v < Version('4.0.0')
        assert v < Version('2.3.9')
        assert v > Version('2.0.0')
        assert v == Version('2.1')

    def test_version_major_minor_patch(self):
        v = Version('2.1.3')
        assert v.major == 2
        assert v.minor == 1
        assert v.patch == 3
        assert v.micro == None
        assert v < Version('4.0.0')
        assert v < Version('2.3.9')
        assert v > Version('2.0.0')
        assert v == Version('2.1.3')

    def test_version_major_minor_patch_micro(self):
        v = Version('2.1.3-c')
        assert v.major == 2
        assert v.minor == 1
        assert v.patch == 3
        assert v.micro == 'c'
        assert v < Version('4.0.0')
        assert v < Version('2.3.9')
        assert v > Version('2.0.0')
        assert v > Version('2.1.3-b')
        assert v < Version('2.1.3-d')
        assert v == Version('2.1.3-c')

class TestModuleArgumentParser:
    def test_arg_parser_no_positional(self):
        p = ModuleArgumentParser()
        with pytest.raises(ValueError):
            p.add_argument('bar')
    def test_arg_parser_bad_action(self):
        p = ModuleArgumentParser()
        with pytest.raises(ValueError):
            p.add_argument('+x', action='count')
    def test_unit(self):
        p = ModuleArgumentParser()
        opt = '{0}b'.format(p.prefix_chars)
        p.add_argument(opt, action='store_true')
        ns = p.parse_args()
        assert not ns.b
        ns = p.parse_args([opt])
        assert ns.b
