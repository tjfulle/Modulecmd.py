import pymod.tutorial
import pymod.modulepath


def test_tutorial_basic():
    pymod.tutorial.basic_usage()
    a = pymod.modulepath.get("A")
    assert a is not None
    pymod.tutorial.teardown()


def test_tutorial_hierarchy():
    pymod.tutorial.hierarchy()
    occ = pymod.modulepath.get("occ")
    assert occ is not None
    pymod.mc.load_impl(occ)

    ompi = pymod.modulepath.get("ompi")
    assert ompi is not None
    pymod.mc.load_impl(ompi)

    z = pymod.modulepath.get("Z")
    assert z is not None

    pymod.tutorial.teardown()
