import modulecmd.system
import modulecmd.tutorial
import modulecmd.modulepath


def test_tutorial_basic():
    modulecmd.tutorial.basic_usage()
    a = modulecmd.modulepath.get("A")
    assert a is not None
    modulecmd.tutorial.teardown()


def test_tutorial_hierarchy():
    modulecmd.tutorial.hierarchy()
    occ = modulecmd.modulepath.get("occ")
    assert occ is not None
    modulecmd.system.load_impl(occ)

    ompi = modulecmd.modulepath.get("ompi")
    assert ompi is not None
    modulecmd.system.load_impl(ompi)

    z = modulecmd.modulepath.get("Z")
    assert z is not None

    modulecmd.tutorial.teardown()
