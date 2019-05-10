import os
import pytest
from pymod.module.argument_parser import ModuleArgumentParser


def test_module_argparse_prefix_chars():
    p = ModuleArgumentParser()
    assert p.prefix_chars == '+'


def test_module_argparse_no_positional():
    p = ModuleArgumentParser()
    with pytest.raises(ValueError):
        p.add_argument('bar')


def test_module_argparse_bad_action():
    p = ModuleArgumentParser()
    with pytest.raises(ValueError):
        p.add_argument('+x', action='count')


def test_module_argparse_basic():
    p = ModuleArgumentParser()
    p.add_argument('+b', action='store_true')
    ns = p.parse_args([])
    assert not ns.b
    ns = p.parse_args(['+b'])
    assert ns.b


def test_module_argparse_help_string():
    p = ModuleArgumentParser()
    p.add_argument('++x', help='Store an x')
    p.add_argument('+a', action='store_true', help='Set an a')
    help_str = 'Module options:\n  ++x X  Store an x\n  +a     Set an a'
    assert help_str == p.help_string().strip()
