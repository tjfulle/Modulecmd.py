import sys
import pymod.config
import pymod.environ
import pymod.modulepath


def format_output():
    """Format the final output for the shell to be evaluated"""
    output = pymod.modulepath.format_output()
    output += pymod.environ.format_output()
    return output


def dump():
    """Dump the final results to the shell to be evaluated"""
    output = format_output()
    if pymod.config.get('dryrun'):
        sys.stderr.write(output)
    else:
        sys.stdout.write(output)
    output = pymod.mc._mc.format_changed_module_state()
    if output.split():
        sys.stderr.write(output)
