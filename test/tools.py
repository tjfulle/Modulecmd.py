import os
import sys
import shutil
import tempfile

sys._pytest_in_progress_ = True
__D = os.path.dirname(os.path.realpath(__file__))
pymod_pkg_dir = os.path.realpath(os.path.join(__D, '../lib'))
assert os.path.isdir(pymod_pkg_dir)
sys.path.insert(0, pymod_pkg_dir)


import pymod
pymod.cfg.cfg.tests_in_progress = True


class TestBase(object):

    def setup_class(self):
        self.datadir = t_make_temp_directory()
        dotdir = os.path.join(self.datadir, 'pymod.d')
        t_make_directory(dotdir)
        os.environ['PYMOD_DOT_DIR'] = dotdir
        pymod.cfg.cfg.dot_dir = dotdir
        self.dotdir = dotdir

    def teardown_class(self):
        t_remove_directory(self.datadir)


def t_remove_directory(dirname):
    if os.path.isdir(dirname):
        shutil.rmtree(dirname)
    return None

def t_make_directory(dirname, wipe_first=False):
    if wipe_first:
        t_remove_directory(dirname)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    return os.path.realpath(dirname)

def t_make_temp_directory(dir=None):
    d = tempfile.mkdtemp(suffix='.d', dir=dir)
    return os.path.realpath(d)

def t_touch(path, wipe_first=False):
    dirname, filename = os.path.split(path)
    if not os.path.isdir(dirname):
        t_make_directory(dirname)
    if wipe_first and os.path.isfile(path):
        os.remove(path)
    with open(path, 'w') as fh:
        fh.write('\n')
    return path

def t_symlink(path, linkname, wipe_first=False):
    dirname, filename = os.path.split(path)
    if not os.path.isfile(path):
        t_touch(path)
    linkpath = os.path.join(dirname, linkname)
    if wipe_first and os.path.exists(linkpath):
        os.remove(linkpath)
    os.symlink(path, linkpath)
    return path

def t_is_executable(path):
    """Is the path executable?"""
    return os.path.exists(path) and os.access(path, os.X_OK)

def t_which(executable, PATH=None):
    """Find path to the executable"""
    if t_is_executable(executable):
        return os.path.realpath(executable)
    PATH = PATH or os.getenv('PATH')
    for d in PATH.split(os.pathsep):
        if not os.path.isdir(d):
            continue
        f = os.path.join(d, executable)
        if t_is_executable(f):
            return f
    return None

def t_controller(modulepath=None, **kwds):
    from pymod.controller import MasterController
    modulepath = kwds.pop('MODULEPATH', modulepath)
    assert modulepath is not None, 'modulepath must be set'
    environ = {}
    for key in ('HOME', 'USER', 'PATH'):
        environ[key] = os.environ[key]
    environ['MODULEPATH'] = modulepath
    environ.update(**kwds)
    return MasterController(env=environ, verbosity=2)

def t_has_tclsh():
    return t_which('tclsh') is not None

t_no_tcl = not t_has_tclsh()
