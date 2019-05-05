import os
import subprocess

import pymod.paths
import pymod.names
import pymod.environ
import contrib.util.logging as logging


def tcl2py(module, mode):
    tcl2py_exe = os.path.join(pymod.paths.bin_path, 'tcl2py.tcl')
    tcl2py = Executable(tcl2py_exe)

    env = dict([item for item in pymod.environ.items() if item[1] is not None])

    mode = {'show': 'display'}.get(mode, mode)
    args = []
    args.extend(('-l', env.get(pymod.names.loaded_modules, '')))
    args.extend(('-f', module.fullname))
    args.extend(('-m', mode))
    args.extend(('-u', module.name))
    args.extend(('-s', 'bash'))

    ldlibname = 'DYLD_LIBRARY_PATH' if IS_DARWIN else 'LD_LIBRARY_PATH'
    ldlib = env.get(ldlibname)
    if ldlib:
        args.extend(('-L', ldlib))

    ld_preload = env.get('LD_PRELOAD')
    if ld_preload:
        args.extend(('-P', ld_preload))

    args.append(module.filename)

    kwargs = {'env': env, 'output': str}
    output = tcl2py(*args, **kwargs)
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
        output = 'family("{0}")\n'.format(family) + output

    return output