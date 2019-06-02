import os
import stat
import shutil
import getpass
import tempfile
import pymod.mc

from appdirs import AppDirs


def destination_root():
    username = getpass.getuser()
    d = os.path.join(tempfile.gettempdir(), username, 'Modulecmd.py')
    return d


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

    basic_dirs = gen_basic_modules(root)

    for basic_dir in basic_dirs[:2]:
        pymod.modulepath.append_path(basic_dir)

    if not pymod.environ.get_dict(pymod.names.tutorial_save_env):
        pymod.environ.set_dict(pymod.names.tutorial_save_env, env)

    pymod.environ.set('PYMOD_TUTORIAL_ROOT_PATH', root)

    return


def teardown():
    env = pymod.environ.get_dict(pymod.names.tutorial_save_env)
    if env:
        root = pymod.environ.get('PYMOD_TUTORIAL_ROOT_PATH')
        pymod.mc.purge(load_after_purge=False)
        pymod.mc.clone.restore_impl(env)
        if root:
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


def sanitize(filename):
    home = os.path.expanduser('~/')
    return filename.replace(home, '~/')


def make_executable(filename):
    st = os.stat(filename)
    os.chmod(filename, st.st_mode | stat.S_IEXEC)


def write_basic_module_and_script(name, version, modulepath, scriptpath):

    fullname = name
    if version is not None:
        fullname = os.path.join(name, version)

    if version is None:
        modulefile = join_path(modulepath, name + '.py')
        scriptfile = join_path(scriptpath, name)
    else:
        modulefile = join_path(modulepath, name, version + '.py')
        scriptfile = join_path(scriptpath, name + '-' + version)

    mkdirp(os.path.dirname(modulefile))
    mkdirp(os.path.dirname(scriptfile))

    with open(modulefile, 'w') as fh:
        fh.write('whatis("Module {0}")\n'.format(name))
        fh.write('\n# Prepend the PATH environment variable with my bin directory\n')
        fh.write("prepend_path('PATH', {0!r})\n".format(sanitize(scriptpath)))
        fh.write('\n# Set an alias to my script\n')
        fh.write("set_alias('s-{0}', {1!r})\n".format(name, sanitize(scriptfile)))

    with open(scriptfile, 'w') as fh:
        fh.write('#!/usr/bin/env sh\n')
        fh.write('echo "This is a script associated with module {0} in {1}"\n'
                 .format(fullname, modulepath))

    make_executable(scriptfile)


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
    """
    modules/basic/1
      A.py
      B.py
      C/1.0.py

    """

    basic_sw_dir = mkdirp(base_dir, 'basic', 'sw')
    basic_modules_dir = mkdirp(base_dir, 'basic', 'modules')

    dirs = []
    for i in range(3):
        modulepath = mkdirp(basic_modules_dir, str(i + 1))
        sw_dir = mkdirp(basic_sw_dir, str(i + 1))

        if i == 0:
            # A exists only in one directory
            name = 'A'
            scriptpath = mkdirp(sw_dir, name, 'bin')
            write_basic_module_and_script(name, None, modulepath, scriptpath)

        name = 'B'
        scriptpath = mkdirp(sw_dir, name, 'bin')
        write_basic_module_and_script(name, None, modulepath, scriptpath)

        name = 'C'
        version = '{0}.0'.format(i + 1)
        scriptpath = mkdirp(sw_dir, name, version, 'bin')
        write_basic_module_and_script(name, version, modulepath, scriptpath)

        dirs.append(modulepath)

    return dirs
