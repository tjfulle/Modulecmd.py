import pytest
import pymod.command.common.parse2 as p


def test_parse2_1():
    args = ['foo@3.1.2']
    modules = p.parse(args)
    assert len(modules) == 1
    assert modules[0]['name'] == 'foo'
    assert modules[0]['version'] == '3.1.2'

    args = ['foo @3.1.2']
    modules = p.parse(args)
    print(modules)
    assert len(modules) == 1
    assert modules[0]['name'] == 'foo'
    assert modules[0]['version'] == '3.1.2'

    args = ['foo/3.1.2']
    modules = p.parse(args)
    assert len(modules) == 1
    assert modules[0]['name'] == 'foo'
    assert modules[0]['version'] == '3.1.2'


def test_parse2_2():
    args =['foo@6.0', '+spam', '-baz', '%gcc@8.3.0', '^openmpi@3.1.2',
           'baz', '@2', 'opt=True', 'foo=x', '~x',
           'bar/4.3.9']
    modules = p.parse(args)
    assert len(modules) == 3

    m = modules[0]
    assert m['name'] == 'foo'
    assert m['version'] == '6.0'
    assert m['opts'] == {'spam': True, 'baz': False}
    assert m['compiler_vendor'] == 'gcc'
    assert m['compiler_version'] == '8.3.0'
    assert m['mpi_vendor'] == 'openmpi'
    assert m['mpi_version'] == '3.1.2'

    m = modules[1]
    assert m['name'] == 'baz'
    assert m['version'] == '2'
    assert m['opts'] == {'opt': True, 'foo': 'x', 'x': False}
    assert m.get('compiler_vendor') is None
    assert m.get('mpi_vendor') is None

    m = modules[2]
    assert m['name'] == 'bar'
    assert m['version'] == '4.3.9'
    assert m.get('opts') is None
    assert m.get('compiler_vendor') is None
    assert m.get('mpi_vendor') is None


def test_parse2_3():
    args =['foo/5/2']
    modules = p.parse(args)
    assert len(modules) == 1
    m = modules[0]
    assert m['name'] == 'foo'
    assert m['version'] == '5'
    assert m['variant'] == '2'

    args =['foo', '@5/2']
    modules = p.parse(args)
    m = modules[0]
    assert m['name'] == 'foo'
    assert m['version'] == '5'
    assert m['variant'] == '2'


def test_parse2_4():
    with pytest.raises(ValueError):
        args =['foo/5/2/5']
        modules = p.parse(args)
    with pytest.raises(ValueError):
        args =['foo@5/2/5']
        modules = p.parse(args)


def test_parse2_5():
    with pytest.raises(ValueError):
        args =['+x']
        modules = p.parse(args)


def test_parse2_6():
    with pytest.raises(ValueError):
        args =['foo/5.0', '@2.0']
        modules = p.parse(args)


def test_parse2_7():
    with pytest.raises(p.IllFormedModuleOptionError):
        args =['foo/5.0', '++x']
        modules = p.parse(args)
    with pytest.raises(p.IllFormedModuleOptionError):
        args =['foo/5.0', '+']
        modules = p.parse(args)
    with pytest.raises(p.IllFormedModuleOptionError):
        args =['foo/5.0', '+1']
        modules = p.parse(args)


def test_parse2_8():
    opt, val = p.parse_item_for_module_option('item')
    assert opt is None


def test_parse2_9():
    with pytest.raises(ValueError):
        args =['%']
        modules = p.parse(args)
    with pytest.raises(ValueError):
        args =['foo', '@']
        modules = p.parse(args)
