import sys
import pymod.mc
from llnl.util.tty.color import colorize

def info(names):
    loaded_modules = pymod.mc.get_loaded_modules()
    for name in names:
        for module in loaded_modules:
            if module.name == name or module.fullname == name:
                s = ('@B{Module:} @*{%s}\n'
                     '  @C{Name:}         %s\n'
                     '  @C{Version:}      %s\n'
                     '  @C{Modulepath:}   %s' % (
                         module.fullname, module.name, module.version,
                         module.modulepath)
                     )
                sys.stderr.write(colorize(s) + '\n')
                break
        else:
            raise ValueError('Module {0} is not loaded'.format(name))