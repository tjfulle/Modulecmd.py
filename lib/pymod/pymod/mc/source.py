import os
import sys
import pymod.shell
import pymod.environ


def source(filename):
    """Source the file `filename`"""
    sourced = pymod.environ.get_path(pymod.names.sourced_files)
    if filename not in sourced:
        # Only source if it hasn't been sourced
        if not os.path.isfile(filename):
            raise ValueError('{0}: no such file to source'.format(filename))
        command = pymod.shell.format_source_command(filename)
        sourced.append(filename)
        pymod.environ.set_path(pymod.names.sourced_files, sourced)
        sys.stdout.write(command + ';\n')
