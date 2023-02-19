import os
import pytest

import modulecmd.system
import modulecmd.error
import modulecmd.environ

compiler_vendor = "ucc"
mpi_vendor = "umpi"
compiler_versions = ("1.0", "2.0")
mpi_versions = ("1.0", "2.0")


"""Test of module hierarchy.

core/
  ucc/1.0.py
  ucc/2.0.py

compiler/
  ucc/
    1.0/
      a/
        1.0.py
      umpi/
        1.0.py
        2.0.py
    2.0/
      a/
        1.0.py
      umpi/
        1.0.py
        2.0.py

mpi/
    ucc/
      1.0/
        umpi/
          1.0/
            b/
              1.0.py

"""


@pytest.fixture()
def hierarchy(tmpdir, namespace, modulecmds):
    m = modulecmds

    # Build the mpi dependent modules
    mpi_base_dir = tmpdir.mkdir("mpi")
    ucc_mpi_base_dir = mpi_base_dir.mkdir(compiler_vendor)
    for compiler_ver in compiler_versions:
        ucc_ver_dir = ucc_mpi_base_dir.mkdir(compiler_ver)
        umpi_base_dir = ucc_ver_dir.mkdir(mpi_vendor)
        for mpi_ver in mpi_versions:
            umpi_ver_dir = umpi_base_dir.mkdir(mpi_ver)
            b = umpi_ver_dir.mkdir("b")
            b.join("1.0.py").write(m.setenv("b", "1.0"))

    # Build the compiler modules that unlock compiler dependent modules
    compiler = tmpdir.mkdir("compiler")
    ucc_compiler_base_dir = compiler.mkdir(compiler_vendor)
    for compiler_ver in compiler_versions:
        ucc_ver_dir = ucc_compiler_base_dir.mkdir(compiler_ver)
        a = ucc_ver_dir.mkdir("a")
        a.join("1.0.py").write(m.setenv("a", "1.0"))

        umpi_base_dir = ucc_ver_dir.mkdir(mpi_vendor)
        for mpi_ver in mpi_versions:
            d = os.path.join(
                mpi_base_dir.strpath, compiler_vendor, compiler_ver, mpi_vendor, mpi_ver
            )
            umpi_base_dir.join(mpi_ver + ".py").write(
                m.setenv(mpi_vendor, mpi_ver) + m.use(d)
            )

    # Build the core modules
    core = tmpdir.mkdir("core")
    ucc_core_base_dir = core.mkdir(compiler_vendor)
    for compiler_ver in compiler_versions:
        d = os.path.join(compiler.strpath, compiler_vendor, compiler_ver)
        assert os.path.exists(d)
        ucc_core_base_dir.join(compiler_ver + ".py").write(
            m.family("compiler") + m.use(d)
        )

    ns = namespace()
    ns.core = core.strpath
    return ns


def test_hierarchy_fixture_layout(hierarchy, mock_modulepath):
    """Loop through the module hierarchy to make sure it is laid out
    correctly"""
    core_path = hierarchy.core
    mock_modulepath(hierarchy.core)

    is_module = lambda x: modulecmd.modulepath.get(x) is not None

    for compiler_ver in compiler_versions:
        compiler_module_name = os.path.sep.join((compiler_vendor, compiler_ver))
        compiler = modulecmd.system.load(compiler_module_name)
        assert compiler is not None

        compiler_unlocks_dir = os.path.normpath(
            os.path.join(core_path, "..", "compiler", compiler_vendor, compiler_ver)
        )

        assert os.path.isdir(compiler_unlocks_dir)
        assert modulecmd.modulepath.contains(compiler_unlocks_dir)

        a = modulecmd.modulepath.get("a")
        assert a is not None
        assert a.version.string == "1.0"
        assert a.file == os.path.join(
            compiler_unlocks_dir, a.name, a.version.string + ".py"
        )

        for mpi_ver in mpi_versions:
            mpi_module_name = os.path.sep.join((mpi_vendor, mpi_ver))
            mpi = modulecmd.system.load(mpi_module_name)
            assert mpi is not None

            mpi_unlocks_dir = os.path.normpath(
                os.path.join(
                    core_path,
                    "..",
                    "mpi",
                    compiler_vendor,
                    compiler_ver,
                    mpi_vendor,
                    mpi_ver,
                )
            )

            assert os.path.isdir(mpi_unlocks_dir)
            assert modulecmd.modulepath.contains(mpi_unlocks_dir)

            modulecmd.system.load("b")

    return


def test_hierarchy_core_compiler_mpi(hierarchy, mock_modulepath):
    """Tests the basic functionality of module hierarchy.

    Steps:
    - Load a compiler.  The compiler unlocks compiler dependent modules
    - Load a compiler dependent module.
    - Load an mpi implementation. The mpi implementation unlocks mpi
      implementation dependent modules
    - Load an mpi implementation dependent module

    Now is the fun part
    - Load a different compiler.

    The compiler dependent and mpi dependent modules will all be updated
    accordingly

    """
    core_path = hierarchy.core
    mock_modulepath(hierarchy.core)

    _compiler_unlocks_dir = lambda cc, cv: os.path.normpath(
        os.path.join(core_path, "..", "compiler", cc, cv)
    )
    _mpi_unlocks_dir = lambda cc, cv, mpi, mpiv: os.path.normpath(
        os.path.join(core_path, "..", "mpi", cc, cv, mpi, mpiv)
    )

    compiler_ver = compiler_versions[0]
    compiler_module_name = os.path.sep.join((compiler_vendor, compiler_ver))
    compiler = modulecmd.system.load(compiler_module_name)
    assert compiler is not None

    compiler_unlocks_dir = _compiler_unlocks_dir(compiler_vendor, compiler_ver)

    assert os.path.isdir(compiler_unlocks_dir)
    assert modulecmd.modulepath.contains(compiler_unlocks_dir)

    a = modulecmd.modulepath.get("a")
    assert a is not None
    assert a.version.string == "1.0"
    assert a.file == os.path.join(
        compiler_unlocks_dir, a.name, a.version.string + ".py"
    )

    mpi_ver = mpi_versions[0]
    mpi_module_name = os.path.sep.join((mpi_vendor, mpi_ver))
    mpi = modulecmd.system.load(mpi_module_name)
    assert mpi is not None
    assert mpi.acquired_as == mpi.fullname

    mpi_unlocks_dir = _mpi_unlocks_dir(
        compiler_vendor, compiler_ver, mpi_vendor, mpi_ver
    )

    assert os.path.isdir(mpi_unlocks_dir)
    assert modulecmd.modulepath.contains(mpi_unlocks_dir)

    b = modulecmd.system.load("b")
    assert b.file == os.path.join(mpi_unlocks_dir, b.name, b.version.string + ".py")

    # Now, load a different compiler and a, mpi, and b modules will all be
    # updated automatically
    compiler_ver = compiler_versions[1]
    compiler_module_name = os.path.sep.join((compiler_vendor, compiler_ver))
    assert mpi.acquired_as == mpi.fullname
    compiler = modulecmd.system.load(compiler_module_name)
    assert compiler is not None
    compiler_unlocks_dir = _compiler_unlocks_dir(compiler_vendor, compiler_ver)
    assert os.path.isdir(compiler_unlocks_dir)
    assert modulecmd.modulepath.contains(compiler_unlocks_dir)

    a = modulecmd.modulepath.get("a")
    assert a.file == os.path.join(
        compiler_unlocks_dir, a.name, a.version.string + ".py"
    )

    mpi = modulecmd.modulepath.get(mpi_module_name)
    assert mpi is not None
    mpi_unlocks_dir = _mpi_unlocks_dir(
        compiler_vendor, compiler_ver, mpi_vendor, mpi_ver
    )
    assert os.path.isdir(mpi_unlocks_dir)
    assert modulecmd.modulepath.contains(mpi_unlocks_dir)

    b = modulecmd.modulepath.get("b")
    assert b.file == os.path.join(mpi_unlocks_dir, b.name, b.version.string + ".py")

    unlocked_by = b.unlocked_by()
    assert len(unlocked_by) == 2
    assert unlocked_by[0] == modulecmd.modulepath.get("ucc/2.0")
    assert unlocked_by[1] == modulecmd.modulepath.get("umpi/1.0")
    return
