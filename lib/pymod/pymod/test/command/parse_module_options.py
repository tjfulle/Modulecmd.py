import pytest
from pymod.command.common.parse_module_options import parse_module_options, IllFormedModuleOptionError

def test_command_parse_module_options_good_1():
    args = ['baz', 'foo=bar', '+spam', '-eggs']
    argv = parse_module_options(args)
    assert len(argv) == 1
    name, opts = argv[0]
    assert name == 'baz'
    assert opts == {'foo': 'bar', 'spam': True, 'eggs': False}


def test_command_parse_module_options_good_2():
    args = ['baz', 'foo=bar', '+spam', '-eggs',
            'foo', 'spam=4', 'eggs=False', '-baz']
    argv = parse_module_options(args)
    assert len(argv) == 2
    name, opts = argv[0]
    assert name == 'baz'
    assert opts == {'foo': 'bar', 'spam': True, 'eggs': False}

    name, opts = argv[1]
    assert name == 'foo'
    assert opts == {'spam': 4, 'eggs': False, 'baz': False}


def test_command_parse_module_options_bad():

    args = ['+spam']
    with pytest.raises(ValueError):
        argv = parse_module_options(args)

    args = ['baz', '+-spam']
    with pytest.raises(IllFormedModuleOptionError):
        argv = parse_module_options(args)

    args = ['baz', '++spam']
    with pytest.raises(IllFormedModuleOptionError):
        argv = parse_module_options(args)

    args = ['baz', '-+spam']
    with pytest.raises(IllFormedModuleOptionError):
        argv = parse_module_options(args)

    args = ['baz', '--spam']
    with pytest.raises(IllFormedModuleOptionError):
        argv = parse_module_options(args)

    args = ['baz', '-1spam']
    with pytest.raises(IllFormedModuleOptionError):
        argv = parse_module_options(args)

    args = ['baz', '-*spam']
    with pytest.raises(IllFormedModuleOptionError):
        argv = parse_module_options(args)

    args = ['baz', '-']
    with pytest.raises(IllFormedModuleOptionError):
        argv = parse_module_options(args)
