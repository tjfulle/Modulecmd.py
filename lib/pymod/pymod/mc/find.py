import sys
import pymod.modulepath
from llnl.util.tty.color import colorize
from pymod.error import ModuleNotFoundError


def find(names):
    all_modules = [m for p in pymod.modulepath.walk() for m in p.modules]
    for name in names:
        s = None
        for module in all_modules:
            if module.name == name or module.fullname == name:
                s = ('@*{%s}\n'
                     '  @C{%s}' % (module.fullname, module.filename)
                     )
                sys.stderr.write(colorize(s) + '\n')
        if s is None:
            raise ModuleNotFoundError(name)