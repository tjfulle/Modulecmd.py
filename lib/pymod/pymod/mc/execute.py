import os
import subprocess
import pymod.environ
import llnl.util.tty as tty
from contrib.util import split
from spack.util.executable import Executable


def execute(command):
    xc = split(command, ' ', 1)
    exe = Executable(xc[0])
    with open(os.devnull, 'a') as fh:
        kwargs = {
            'env': pymod.environ.filtered(),
            'output': fh,
            'error': subprocess.sys.stdout,
        }
        try:
            exe(*xc[1:], **kwargs)
        except:
            tty.warn('Command {0!r} failed'.format(command))
    return
