import pytest

import modulecmd.system
import modulecmd.modes
import modulecmd.names
import modulecmd.environ
import modulecmd.modulepath


@pytest.fixture()
def modules_path(tmpdir):
    basic_py_module = """\
family('XYZ')
setenv('ENVAR_1', self.name)
setenv('ENVAR_2', self.version.string)"""
    a = tmpdir.mkdir("A")
    a.join("1.0.py").write(basic_py_module)
    a.join("2.0.py").write(basic_py_module)
    b = tmpdir.mkdir("B")
    b.join("1.0.py").write(basic_py_module)
    b.join("2.0.py").write(basic_py_module)
    return tmpdir.strpath


def test_mc_family_load_1(mock_module):
    family = "compiler"
    module = mock_module("ucc", "1.2", "ucc/1.2.py")
    modulecmd.system.family(module, modulecmd.modes.load, "compiler")
    assert modulecmd.environ.environ["MODULE_FAMILY_COMPILER"] == "ucc"
    assert modulecmd.environ.environ["MODULE_FAMILY_COMPILER_VERSION"] == "1.2"


def test_mc_family_unload_1(mock_module):
    module = mock_module("ucc", "2.0", "ucc/2.0.py")
    modulecmd.environ.set("MODULE_FAMILY_COMPILER", "ucc")
    modulecmd.environ.set("MODULE_FAMILY_UCC_VERSION", "2.0")
    modulecmd.system.family(module, modulecmd.modes.unload, "compiler")
    assert modulecmd.environ.environ["MODULE_FAMILY_COMPILER"] is None
    assert modulecmd.environ.environ["MODULE_FAMILY_COMPILER_VERSION"] is None


def test_mc_family_xyz(modules_path, mock_modulepath, get_loaded_modules):
    def standard_assertions(module):
        name_key = modulecmd.names.family_name("xyz")
        ver_key = modulecmd.names.family_version("xyz")
        assert modulecmd.environ.environ[name_key] == module.name
        assert modulecmd.environ.environ[ver_key] == module.version.string
        assert modulecmd.environ.environ["ENVAR_1"] == module.name
        assert modulecmd.environ.environ["ENVAR_2"] == module.version.string
        loaded_modules = get_loaded_modules()
        print(loaded_modules)
        for key in ("A", "B"):
            for ver in ("1.0", "2.0"):
                id = "{0}/{1}".format(key, ver)
                if id == module.fullname:
                    assert id in loaded_modules
                else:
                    assert id not in loaded_modules

    mock_modulepath(modules_path)

    a1 = modulecmd.modulepath.get("A/1.0")
    assert a1 is not None
    modulecmd.system.load_impl(a1)
    print(modulecmd.system.state.loaded_modules)
    standard_assertions(a1)

    a2 = modulecmd.modulepath.get("A/2.0")
    assert a2 is not None
    modulecmd.system.load_impl(a2)
    standard_assertions(a2)

    old, new = modulecmd.system.state._swapped_on_version_change[0]
    assert old.fullname == "A/1.0"
    assert new.fullname == "A/2.0"

    b1 = modulecmd.modulepath.get("B/1.0")
    assert b1 is not None
    modulecmd.system.load_impl(b1)
    standard_assertions(b1)

    old, new = modulecmd.system.state._swapped_on_family_update[0]
    assert old.fullname == "A/2.0"
    assert new.fullname == "B/1.0"

    b2 = modulecmd.modulepath.get("B/2.0")
    assert b2 is not None
    modulecmd.system.load_impl(b2)
    standard_assertions(b2)

    old, new = modulecmd.system.state._swapped_on_version_change[1]
    assert old.fullname == "B/1.0"
    assert new.fullname == "B/2.0"
