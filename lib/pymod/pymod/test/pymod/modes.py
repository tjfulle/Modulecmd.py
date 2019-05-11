import pymod.modes


def test_modes():
    mode = pymod.modes.get_mode('whatis')
    assert mode == pymod.modes.whatis
    mode = pymod.modes.get_mode('fake')
    assert mode is None

    assert pymod.modes.as_string(pymod.modes.load) == 'load'
