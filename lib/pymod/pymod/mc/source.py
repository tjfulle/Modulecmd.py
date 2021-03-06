import os
import sys
import pymod.shell
import pymod.environ


def source(filename, *args):
    """Source the file `filename`"""
    sourced = pymod.environ.get_path(pymod.names.sourced_files)
    if filename not in sourced:
        # Only source if it hasn't been sourced
        if not os.path.isfile(filename):
            raise ValueError("{0}: no such file to source".format(filename))
        sourced.append(filename)
        pymod.environ.set_path(pymod.names.sourced_files, sourced)
        pymod.environ.source_file(filename, *args)
