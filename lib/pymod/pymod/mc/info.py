import sys
import pymod.mc
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
            s += '  @C{Filename:}     %s\n' % module.filename
            s += '  @C{Modulepath:}   %s' % module.modulepath

            unlocked_by = module.unlocked_by()
            if unlocked_by:  # pragma: no cover
                s += '  @C{Unlocked by:}  %s\n'
                for m in unlocked_by:
                    s += '                    %s\n' % m.fullname

            unlocks = module.unlocks()
            if unlocks:  # pragma: no cover
                s += '  @C{Unlocks:}      %s\n'
                for dirname in unlocks:
                    s += '                    %s\n' % dirname

            sys.stderr.write(colorize(s) + '\n')
