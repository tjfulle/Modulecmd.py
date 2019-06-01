import os
import shutil
import pymod.mc

from appdirs import AppDirs


def destination_root():
    appdirs = AppDirs('Modulecmd.py')
    return appdirs.user_data_dir


def intermediate():

    env = pymod.environ.copy(include_os=True)
    pymod.mc.purge(load_after_purge=False)
    pymod.modulepath.clear()

    root = destination_root()

    rmdir(root)
    mkdirp(root)

    core_base_dir = mkdirp(root, 'core')
    compiler_base_dir = mkdirp(root, 'compiler')
    mpi_base_dir = mkdirp(root, 'mpi')

    compilers = [('occ', ('6.0', '7.0')),
                 ('pcc', ('2016.01', '2017.02'))]
    mpis = [('ompi', ('1.0', '2.0'))]

    gen_core_modules(core_base_dir, compiler_base_dir, compilers)
    gen_compiler_dep_modules(compiler_base_dir, mpi_base_dir, compilers, mpis)
    gen_mpi_dep_modules(mpi_base_dir, compilers, mpis)

    pymod.modulepath.append_path(core_base_dir)

    if not pymod.environ.get_dict(pymod.names.tutorial_save_env):
        pymod.environ.set_dict(pymod.names.tutorial_save_env, env)

    return


def basic():
    env = pymod.environ.copy(include_os=True)
    pymod.mc.purge(load_after_purge=False)
    pymod.modulepath.clear()
    root = destination_root()

    rmdir(root)
    mkdirp(root)

    basic_base_dir = mkdirp(root, 'basic')
    basic_dirs = gen_basic_modules(basic_base_dir)

    for basic_dir in basic_dirs:
        pymod.modulepath.append_path(basic_dir)

    if not pymod.environ.get_dict(pymod.names.tutorial_save_env):
        pymod.environ.set_dict(pymod.names.tutorial_save_env, env)

    return


def teardown():
    env = pymod.environ.get_dict(pymod.names.tutorial_save_env)
    if env:
        pymod.mc.purge(load_after_purge=False)
        pymod.mc.clone.restore_impl(env)
        root = destination_root()
        rmdir(root)


def join_path(*paths):
    return os.path.join(*paths)


def mkdirp(*paths):
    path = os.path.join(*paths)
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def rmdir(d):
    if os.path.isdir(d):
        shutil.rmtree(d)


def gen_mpi_dep_modules(mpi_base_dir, compilers, mpis):

    # Build the mpi dependent modules
    for (mpi_vendor, mpi_versions) in mpis:
        for mpi_version in mpi_versions:
            for (compiler_vendor, compiler_versions) in compilers:
                for compiler_version in compiler_versions:
                    dest_dir = mkdirp(mpi_base_dir, compiler_vendor,
                                      compiler_version, mpi_vendor, mpi_version)

                    # Write
                    for name in 'XYZ':
                        module_dir = mkdirp(dest_dir, name)
                        for version in ('2.0', '3.0'):
                            with open(join_path(module_dir, version+'.py'), 'w') as fh:
                                fh.write("setenv({0!r}, '{0}/{1}-{2}/{3}-{4}/{5}')\n"
                                         .format(name, version,
                                                 compiler_vendor, compiler_version,
                                                 mpi_vendor, mpi_version))



def gen_compiler_dep_modules(compiler_base_dir, mpi_base_dir, compilers, mpis):

    # Build the compiler modules that unlock compiler dependent modules
    for (compiler_vendor, compiler_versions) in compilers:
        for compiler_version in compiler_versions:
            dest_dir = mkdirp(compiler_base_dir, compiler_vendor, compiler_version)
            for name in 'QRS':
                module_dir = mkdirp(dest_dir, name)
                for version in ('1.0', '2.0'):
                    with open(join_path(module_dir, version+'.py'), 'w') as fh:
                        fh.write("setenv({0!r}, '{0}/{1}-{2}/{3}')\n"
                                 .format(name, version, compiler_vendor, compiler_version))

            # MPI unlock modules
            for (mpi_vendor, mpi_versions) in mpis:
                module_dir = mkdirp(dest_dir, mpi_vendor)
                for mpi_version in mpi_versions:
                    unlocks = os.path.join(mpi_base_dir, compiler_vendor,
                                           compiler_version, mpi_vendor, mpi_version)
                    with open(join_path(module_dir, mpi_version+'.py'), 'w') as fh:
                        fh.write("family('mpi')\n")
                        fh.write("use({0!r})\n".format(unlocks))


def gen_core_modules(core_base_dir, compiler_base_dir, compilers):

    # Build the core modules
    for name in 'AB':
        with open(join_path(core_base_dir, name+'.py'), 'w') as fh:
            fh.write("setenv({0!r}, {0!r})\n".format(name))

    for name in 'CD':
        module_dir = mkdirp(core_base_dir, name)
        for version in ('1.0', '2.0'):
            with open(join_path(module_dir, version+'.py'), 'w') as fh:
                fh.write("setenv({0!r}, '{0}/{1}')\n"
                         .format(name, version))

    for (vendor, versions) in compilers:
        module_dir = mkdirp(core_base_dir, vendor)
        for version in versions:
            unlocks = join_path(compiler_base_dir, vendor, version)
            with open(join_path(module_dir, version+'.py'), 'w') as fh:
                fh.write("family('compiler')\n")
                fh.write("use({0!r})\n".format(unlocks))


def gen_basic_modules(base_dir):

    d1 = mkdirp(base_dir, '1')

    with open(join_path(d1, 'A.py'), 'w') as fh:
        fh.write("setenv('A', 'A-1')\n")

    with open(join_path(d1, 'B.py'), 'w') as fh:
        fh.write("setenv('B', 'B-1')\n")

    C = mkdirp(d1, 'C')
    for version in ('1.0', '2.0'):
        with open(join_path(C, version+'.py'), 'w') as fh:
            fh.write("setenv('C', 'C-1-{0}')\n".format(version))

    # Second
    d2 = mkdirp(base_dir, '2')

    with open(join_path(d2, 'B.py'), 'w') as fh:
        fh.write("setenv('B', 'B-2')\n")

    C = mkdirp(d2, 'C')
    for version in ('1.0', '3.0'):
        with open(join_path(C, version+'.py'), 'w') as fh:
            fh.write("setenv('C', 'C-2-{0}')\n".format(version))

    return d1, d2
