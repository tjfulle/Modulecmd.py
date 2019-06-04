import sys
import pymod.modulepath
from llnl.util.tty.color import colorize
from pymod.error import ModuleNotFoundError

def info(names):
    for name in names:
        modules = pymod.modulepath.candidates(name)
        if not modules:
            raise ModuleNotFoundError(name)

        for module in modules:
            s  = '@B{Module:} @*{%s}\n' % module.fullname
            s += '  @C{Name:}         %s\n' % module.name

            if module.version:  # pragma: no cover
                s += '  @C{Version:}      %s\n' % module.version

            if module.family:  # pragma: no cover
                s += '  @C{Family:}      %s\n' % module.family

            s += '  @C{Loaded:}       %s\n' % module.is_loaded
            s += '  @C{Modulepath:}   %s' % module.modulepath

            sys.stderr.write(colorize(s) + '\n')
