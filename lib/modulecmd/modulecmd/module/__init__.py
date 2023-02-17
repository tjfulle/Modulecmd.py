import os

import modulecmd.config
from modulecmd.module.module import *

import llnl.util.tty as tty


def factory(root, path):
    file = os.path.join(root, path)
    if not ismodule(file):
        return None
    if is_tcl_module(file):
        module_type = TclModule
    elif file.endswith(".py"):
        module_type = PyModule
    module = module_type(root, path)
    if modulecmd.config.get("debug"):  # pragma: no cover
        if module_type == TclModule and "gcc" in file:
            tty.debug(module.name)
            tty.debug(module.modulepath)
            tty.debug(module.filename, "\n")

    return module


def as_dict(module):
    return {
        "type": type(module).__name__,
        "file": module.filename,
        "modulepath": module.modulepath,
    }


def from_dict(dikt):
    filename = dikt["file"]
    root = dikt["modulepath"]
    assert filename.startswith(root)
    path = filename.replace(root + os.path.sep, "")
    module_type = {"PyModule": PyModule, "TclModule": TclModule}[dikt["type"]]
    try:
        module = module_type(root, path)
    except IOError:
        return None
    assert module.filename == filename
    return module


def is_tcl_module(filename):
    tcl_header = "#%Module"
    try:
        return open(filename).readline().startswith(tcl_header)
    except (IOError, UnicodeDecodeError):  # pragma: no cover
        return False


def ishidden(file: str) -> bool:
    return os.path.basename(file).startswith(".")


def ismodule(file: str) -> bool:
    if file.endswith(("~",)) or file.startswith((".#",)):  # pragma: no cover
        # Don't read backup files
        return False
    if file.endswith(".py"):
        return True
    elif is_tcl_module(file):
        return True
    return False
