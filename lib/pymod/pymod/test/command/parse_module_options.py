import pytest
from pymod.command.common.parse_module_options import parse_module_options
from pymod.command.common.parse_module_options import IllFormedModuleOptionError
from pymod.command.common.parse_module_options import parse_item_for_module_option

def test_command_parse_module_options_good_1():
    args = ['baz', 'foo=bar', '+spam', '-eggs']
    argv = parse_module_options(args)
    assert len(argv) == 1
    spec = argv[0]
    assert spec['name'] == 'baz'
    assert spec['options'] == {'foo': 'bar', 'spam': True, 'eggs': False}


def test_command_parse_module_options_good_2():
    args = ['baz', 'foo=bar', '+spam', '-eggs',
            'foo', 'spam=4', 'eggs=False', '-baz']
    argv = parse_module_options(args)
    assert len(argv) == 2
    name, opts = argv[0]['name'], argv[0]['options']
    assert name == 'baz'
    assert opts == {'foo': 'bar', 'spam': True, 'eggs': False}

    name, opts = argv[1]['name'], argv[1]['options']
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


def test_command_parse_module_options_spack_ver():
    args = ['baz@1.2']
    argv = parse_module_options(args)
    assert len(argv) == 1
    name, version = argv[0]['name'], argv[0]['version']
    assert name == 'baz'
    assert version == '1.2'

    args = ['baz', '@1.2']
    argv = parse_module_options(args)
    assert len(argv) == 1
    name, version = argv[0]['name'], argv[0]['version']
    assert name == 'baz'
    assert version == '1.2'

    with pytest.raises(ValueError):
        args = ['@5.4']
        argv = parse_module_options(args)

    with pytest.raises(ValueError):
        args = ['baz', '@']
        argv = parse_module_options(args)


def test_command_parse_module_options_extended_1():
    args = ['foo@3.1.2']
    modules = parse_module_options(args)
    assert len(modules) == 1
    assert modules[0]['name'] == 'foo'
    assert modules[0]['version'] == '3.1.2'

    args = ['foo @3.1.2']
    modules = parse_module_options(args)
    print(modules)
    assert len(modules) == 1
    assert modules[0]['name'] == 'foo'
    assert modules[0]['version'] == '3.1.2'

    args = ['foo/3.1.2']
    modules = parse_module_options(args)
    assert len(modules) == 1
    assert modules[0]['name'] == 'foo/3.1.2'
    assert modules[0]['version'] is None


def test_command_parse_module_options_extended_2():
    args = ['foo@6.0', '+spam', '-baz', '%gcc@8.3.0', '^openmpi@3.1.2',
            'baz', '@2', 'opt=True', 'foo=x', '~x',
            'bar/4.3.9']
    modules = parse_module_options(args)
    assert len(modules) == 3

    m = modules[0]
    assert m['name'] == 'foo'
    assert m['version'] == '6.0'
    assert m['options'] == {'spam': True, 'baz': False}
    assert m['compiler_vendor'] == 'gcc'
    assert m['compiler_version'] == '8.3.0'
    assert m['mpi_vendor'] == 'openmpi'
    assert m['mpi_version'] == '3.1.2'

    m = modules[1]
    assert m['name'] == 'baz'
    assert m['version'] == '2'
    assert m['options'] == {'opt': True, 'foo': 'x', 'x': False}
    assert m.get('compiler_vendor') is None
    assert m.get('mpi_vendor') is None

    m = modules[2]
    assert m['name'] == 'bar/4.3.9'
    assert m['version'] is None
    assert m['options'] == {}
    assert m.get('compiler_vendor') is None
    assert m.get('mpi_vendor') is None


def test_command_parse_module_options_extended_3():
    args = ['foo/5/2']
    modules = parse_module_options(args)
    assert len(modules) == 1
    m = modules[0]
    assert m['name'] == 'foo/5/2'
    assert m['version'] is None

    args = ['foo', '@5/2']
    modules = parse_module_options(args)
    m = modules[0]
    assert m['name'] == 'foo'
    assert m['version'] == '5/2'


def test_command_parse_module_options_extended_4():
    with pytest.raises(ValueError):
        # Too many / in version string
        args = ['foo@5/2/5']
        modules = parse_module_options(args)


def test_command_parse_module_options_extended_5():
    with pytest.raises(ValueError):
        # Option with no preceeding module
        args = ['+x']
        modules = parse_module_options(args)


def test_command_parse_module_options_extended_6():
    # Seems like duplicate versions, but maybe it is foo/5.0 at variant 2.0?
    args = ['foo/5.0', '@2.0']
    modules = parse_module_options(args)
    assert modules[0]['name'] == 'foo/5.0'
    assert modules[0]['version'] == '2.0'


def test_command_parse_module_options_extended_7():
    with pytest.raises(IllFormedModuleOptionError):
        # Bad option
        args = ['foo/5.0', '++x']
        modules = parse_module_options(args)
    with pytest.raises(IllFormedModuleOptionError):
        # Bad option
        args = ['foo/5.0', '+']
        modules = parse_module_options(args)
    with pytest.raises(IllFormedModuleOptionError):
        # Bad option
        args = ['foo/5.0', '+1']
        modules = parse_module_options(args)


def test_command_parse_module_options_extended_8():
    opt, val = parse_item_for_module_option('item')
    assert opt is None


def test_command_parse_module_options_extended_9():
    with pytest.raises(ValueError):
        # No mpi spec follows
        args = ['%']
        modules = parse_module_options(args)
    with pytest.raises(ValueError):
        # No version follows
        args = ['foo', '@']
        modules = parse_module_options(args)


def test_command_parse_module_options_extended_10():
    args = ['foo@6.0', '+spam', '-baz', '%gcc@8.3.0', '^openmpi@3.1.2', ':/foo/bar/baz']
    modules = parse_module_options(args)
    assert len(modules) == 1

    m = modules[0]
    assert m['name'] == 'foo'
    assert m['version'] == '6.0'
    assert m['options'] == {'spam': True, 'baz': False}
    assert m['compiler_vendor'] == 'gcc'
    assert m['compiler_version'] == '8.3.0'
    assert m['mpi_vendor'] == 'openmpi'
    assert m['mpi_version'] == '3.1.2'
    assert m['hint'] == '/foo/bar/baz'
