import os

import pymod.mc
import pymod.names
import pymod.environ
import pymod.modulepath
from pymod.tutorial.common import destination_root, mkdirp, rmdir
from pymod.tutorial.common import join_path, make_executable, sanitize


def basic_usage():

    env = pymod.environ.copy(include_os=True)
    pymod.mc.purge(load_after_purge=False)
    pymod.modulepath.clear()
    root = destination_root()

    rmdir(root)
    mkdirp(root)

    basic_dirs = gen_basic_modules(root)

    for basic_dir in basic_dirs[:2]:
        pymod.modulepath.append_path(basic_dir)

    if not pymod.environ.get(pymod.names.tutorial_save_env, serialized=True):
        pymod.environ.set(pymod.names.tutorial_save_env, env, serialize=True)

    pymod.environ.set(pymod.names.tutorial_root_path, root)

    return


def write_basic_module_and_script(name, version, modulepath, scriptpath):

    fullname = name
    if version is not None:
        fullname = join_path(name, version)

    if version is None:
        scriptname = "script-{0}".format(name).lower()
    else:
        scriptname = "script-{0}-{1}".format(name, version).lower()

    modulefile = join_path(modulepath, fullname + ".py")
    scriptfile = join_path(scriptpath, scriptname)

    mkdirp(os.path.dirname(modulefile))
    mkdirp(os.path.dirname(scriptfile))

    with open(modulefile, "w") as fh:
        fh.write("\n# Prepend the PATH environment variable with my bin directory\n")
        fh.write("prepend_path('PATH', {0!r})\n".format(sanitize(scriptpath)))

    with open(scriptfile, "w") as fh:
        fh.write("#!/usr/bin/env sh\n")
        fh.write(
            'echo "This is a script associated with module {0} in {1}"\n'.format(
                fullname, modulepath
            )
        )

    make_executable(scriptfile)


def gen_basic_modules(base_dir):
    """
    modules/basic/1
      A.py
      B.py
      C/1.0.py
    modules/basic/2
      A.py
      B.py
      C/2.0.py

    """

    basic_sw_dir = mkdirp(base_dir, "basic", "sw")
    basic_modules_dir = mkdirp(base_dir, "basic", "modules")

    dirs = []
    for i in range(3):
        modulepath = mkdirp(basic_modules_dir, str(i + 1))
        sw_dir = mkdirp(basic_sw_dir, str(i + 1))

        if i == 0:
            # A exists only in one directory
            name = "A"
            scriptpath = mkdirp(sw_dir, name, "bin")
            write_basic_module_and_script(name, None, modulepath, scriptpath)

        name = "B"
        scriptpath = mkdirp(sw_dir, name, "bin")
        write_basic_module_and_script(name, None, modulepath, scriptpath)

        name = "C"
        version = "{0}.0".format(i + 1)
        scriptpath = mkdirp(sw_dir, name, version, "bin")
        write_basic_module_and_script(name, version, modulepath, scriptpath)

        dirs.append(modulepath)

    return dirs
