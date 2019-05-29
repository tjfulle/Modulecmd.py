from pymod.module.version import Version


def test_module_version_major():
    v = Version('2')
    assert v.major == 2
    assert v.minor == v.patch == v.variant == None
    assert v < Version('4.0.0')
    assert v < Version('2.3.9')
    assert v > Version('1.0.0')
    assert v == Version('2')


def test_module_version_major_minor():
    v = Version('2.1')
    assert v.major == 2
    assert v.minor == 1
    assert v.patch == v.variant == None
    assert v < Version('4.0.0')
    assert v < Version('2.3.9')
    assert v > Version('2.0.0')
    assert v == Version('2.1')


def test_module_version_major_minor_patch():
    v = Version('2.1.3')
    assert v.major == 2
    assert v.minor == 1
    assert v.patch == 3
    assert v.variant == None
    assert v < Version('4.0.0')
    assert v < Version('2.3.9')
    assert v > Version('2.0.0')
    assert v == Version('2.1.3')


def test_module_version_major_minor_patch_variant():
    v = Version('2.1.3-c')
    assert v.major == 2
    assert v.minor == 1
    assert v.patch == 3
    assert v.variant == 'c'
    assert v < Version('4.0.0')
    assert v < Version('2.3.9')
    assert v > Version('2.0.0')
    assert v > Version('2.1.3-b')
    assert v < Version('2.1.3-d')
    assert v == Version('2.1.3-c')


def test_module_version_bool():
    v = Version()
    assert not v
    assert not v.__nonzero__()
    assert not v.__bool__()


def test_module_version_different():
    v1 = Version('1.68')
    v2 = Version('1.68b')
    assert v2 > v1


def test_module_version_str_v_int():
    v1 = Version('1.0')
    v2 = Version('a')
    assert v2 > v1
