import sys
import pymod.config
import pymod.environ
from llnl.util.tty.color import colorize


def format_output():  # pragma: no cover
    """Format the final output for the shell to be evaluated"""
    output = pymod.environ.format_output()
    return output


def dump(stream=None):  # pragma: no cover
    """Dump the final results to the shell to be evaluated"""
    output = format_output()
    stream = sys.stderr if pymod.config.get("dryrun") else stream or sys.stdout
    stream.write(output)

    output = pymod.mc._mc.format_changed_module_state()
    if output.split():
        sys.stderr.write(colorize(output))
