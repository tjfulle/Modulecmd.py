from pymod.module.version import Version


def test_version():
    version_a = Version('1.2.3-a')
    assert version_a.major == 1
    assert version_a.minor == 2
    assert version_a.patch == 3
    assert version_a.micro == 'a'
    version_b = Version('1.0.0-b')
    assert version_b > version_a
    assert not (version_b < version_a)
    assert not (version_b == version_a)

    assert version_a == Version('1.2.3-a')
