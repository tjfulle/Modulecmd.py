import pymod.mc
import pymod.modulepath


def test_tutorial_basic():
    pymod.mc.tutorial.basic()
    a = pymod.modulepath.get('A')
    assert a is not None
    pymod.mc.tutorial.teardown()


def test_tutorial_intermediate():
    pymod.mc.tutorial.intermediate()
    occ = pymod.modulepath.get('occ')
    assert occ is not None
    pymod.mc.load_impl(occ)

    ompi = pymod.modulepath.get('ompi')
    assert ompi is not None
    pymod.mc.load_impl(ompi)

    z = pymod.modulepath.get('Z')
    assert z is not None

    pymod.mc.tutorial.teardown()
