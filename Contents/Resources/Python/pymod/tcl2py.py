import os
import subprocess

from .constants import *
from .resources import scripts_dir
from .defaults import LM_KEY


def tcl2py(module, mode, env):
    tcl2py_exe = os.path.join(scripts_dir, 'tcl2py.tcl')
    if not os.path.isfile(tcl2py_exe):
        logging.error('Missing required tcl to python converter tcl2py.tcl!')

    env = dict([item for item in env.items() if item[1] is not None])

    mode = {'show': 'display'}.get(mode, mode)
    command = [tcl2py_exe]
    command.extend(('-l', env.get(LM_KEY, '')))
    command.extend(('-f', module.fullname))
    command.extend(('-m', mode))
    command.extend(('-u', module.name))
    command.extend(('-s', 'bash'))

    ldlibname = 'DYLD_LIBRARY_PATH' if IS_DARWIN else 'LD_LIBRARY_PATH'
    ldlib = env.get(ldlibname)
    if ldlib:
        command.extend(('-L', ldlib))

    ld_preload = env.get('LD_PRELOAD')
    if ld_preload:
        command.extend(('-P', ld_preload))

    command.append(module.filename)

    p = subprocess.Popen(command, env=env,
                         stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    comm = p.communicate()
    try:
        stdout, stderr = [x.decode('utf-8', 'ignore') for x in comm]
    except (AttributeError, TypeError):
        stdout, stderr = comm

    name = module.name
    family = None
    #if name.endswith('python'):
    #    family = 'python'
    #elif name.startswith(('gcc', 'intel', 'pgi')):
    #    family = 'compiler'
    #elif name.startswith(('openmpi', 'mpich', )):
    #    family = 'mpi'
    #else:
    #    family = None

    if family is not None:
        stdout = 'family("{0}")\n'.format(family) + stdout

    return stdout


