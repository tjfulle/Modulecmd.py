import modulecmd.modes


def test_modes():
    mode = modulecmd.modes.get_mode("whatis")
    assert mode == modulecmd.modes.whatis
    mode = modulecmd.modes.get_mode("fake")
    assert mode is None

    assert modulecmd.modes.as_string(modulecmd.modes.load) == "load"
