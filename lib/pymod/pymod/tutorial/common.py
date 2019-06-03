import os
import stat
import shutil
import getpass
import tempfile


def destination_root():
    username = getpass.getuser()
    d = os.path.join(tempfile.gettempdir(), username, 'Modulecmd.py')
    return d


def join_path(*paths):
    return os.path.join(*paths)


def mkdirp(*paths):
    path = os.path.join(*paths)
    if os.path.exists(path) and not os.path.isdir(path):  # pragma: no cover
        raise ValueError('Expected path to not exist or be a directory')
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
