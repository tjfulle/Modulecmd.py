import os

import pymod.config
from pymod.module.module import *

import llnl.util.tty as tty


def module(dirname, *parts):
    filename = os.path.join(dirname, *parts)
    if not os.path.isfile(filename):  # pragma: no cover
        tty.verbose('{0} does not exist'.format(filename))
        return None
    elif filename.endswith(('~',)) or filename.startswith(('.#',)):  # pragma: no cover
        # Don't read backup files
        return None

    if filename.endswith('.py'):
        module_type = PyModule
    elif is_tcl_module(filename):
        module_type = TclModule
    else:
        return None

    module = module_type(dirname, *parts)
    if pymod.config.get('debug'):  # pragma: no cover
        if module_type == TclModule and 'gcc' in filename:
            tty.debug(module.name)
            tty.debug(module.modulepath)
            tty.debug(module.filename, '\n')

    return module


def as_dict(module):
    return {'type': type(module).__name__,
            'file': module.filename,
            'modulepath': module.modulepath, }


def from_dict(dikt):
    filename = dikt['file']
    modulepath = dikt['modulepath']
    assert filename.startswith(modulepath)
    parts = filename[(len(modulepath)+1):].split(os.path.sep)
    module_type = {'PyModule': PyModule, 'TclModule': TclModule}[dikt['type']]
    try:
        module = module_type(modulepath, *parts)
    except IOError:
        return None
    assert module.filename == filename
    return module


def is_tcl_module(filename):
    tcl_header = '#%Module'
    try:
        return open(filename).readline().startswith(tcl_header)
    except (IOError, UnicodeDecodeError):  # pragma: no cover
        return False
