import sys
import pymod.modulepath
from llnl.util.tty.color import colorize
from pymod.error import ModuleNotFoundError


def find(names):
    all_modules = [m for p in pymod.modulepath.walk() for m in p.modules]
    for name in names:
        s = None
        candidates = pymod.modulepath.candidates(name)
        if not candidates:
            raise ModuleNotFoundError(name)
        for module in candidates:
            s = '@*{%s}\n  @C{%s}' % (module.fullname, module.filename)
            sys.stderr.write(colorize(s) + '\n')
