import os

import modulecmd.system
import modulecmd.modes
import modulecmd.paths
import modulecmd.names
import modulecmd.environ
from spack.util.executable import Executable


def tcl2py(module, mode):
    tcl2py_exe = os.path.join(modulecmd.paths.bin_path, "tcl2py.tcl")
    tcl2py = Executable(tcl2py_exe)

    env = modulecmd.environ.filtered(include_os=True)

    mode = modulecmd.modes.as_string(mode)
    mode = {"show": "display"}.get(mode, mode)

    args = []
    # loaded modules
    loaded_modules = modulecmd.system.loaded_modules()
    lm_names = list(set([x for m in loaded_modules for x in [m.name, m.fullname]]))
    args.extend(("-l", ":".join(lm_names)))
    args.extend(("-f", module.fullname))
    args.extend(("-m", mode))
    args.extend(("-u", module.name))
    args.extend(("-s", "bash"))

    ldlib = env.get(modulecmd.names.platform_ld_library_path)
    if ldlib:
        args.extend(("-L", ldlib))

    ld_preload = env.get(modulecmd.names.ld_preload)
    if ld_preload:
        args.extend(("-P", ld_preload))

    args.append(module.filename)

    kwargs = {"env": env, "output": str}
    output = tcl2py(*args, **kwargs)
    #  name = module.name
    #  family = None
    #  if name.endswith('python'):
    #      family = 'python'
    #  elif name.startswith(('gcc', 'intel', 'pgi')):
    #      family = 'compiler'
    #  elif name.startswith(('openmpi', 'mpich', )):
    #      family = 'mpi'
    #  else:
    #      family = None
    #
    #  if family is not None:
    #      output = 'family("{0}")\n'.format(family) + output
    return output
