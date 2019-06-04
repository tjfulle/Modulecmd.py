import os
from six import StringIO
from textwrap import fill
from enum_backport import Enum

import pymod.environ
import pymod.config
import pymod.names
from pymod.module.meta import MetaData
from pymod.module.tcl2py import tcl2py
from pymod.module.version import Version

from contrib.util import split, textfill, encode_str
import llnl.util.tty as tty
from llnl.util.tty import terminal_size
from pymod.module.argument_parser import ModuleArgumentParser


# --------------------------------------------------------------------------- #
# --------------------------- MODULE CLASS ---------------------------------- #
# --------------------------------------------------------------------------- #
class Module(object):
    ext = None
    def __init__(self, modulepath, *parts):
        self.filename = os.path.join(modulepath, *parts)
        if self.ext:
            self.filename += self.ext
        if not os.path.isfile(self.filename):
            raise ValueError('{0} is not a file'.format(self.filename))
        version = variant = None
        if len(parts) == 1:
            self.name, = parts
        elif len(parts) == 2:
            self.name, version = parts
        elif len(parts) == 3:
            self.name, version, variant = parts
        else:
            raise ValueError('Too many parts to construct module definition')
        self.version = Version(version)
        self.variant = Version(variant)

        self.modulepath = modulepath
        self.parser = ModuleArgumentParser()
        self.family = None
        self.whatisstr = ''
        self.helpstr = None
        self.is_default = False
        self._opts = None
        self._unlocks = []
        self.marked_as_default = False
        self._acquired_as = None  # How the module was initially loaded
        self._refcount = 0

    def __str__(self):
        return 'Module(name={0})'.format(self.fullname)

    def __repr__(self):
        return 'Module(name={0})'.format(self.fullname)

    @property
    def is_loaded(self):
        lm_files = [m.filename for m in pymod.mc.get_loaded_modules()]
        return self.filename in lm_files

    @property
    def is_enabled(self):
        return True

    @property
    def is_hidden(self):
        return not self.is_enabled

    @property
    def do_not_register(self):
        return False

    @property
    def acquired_as(self):
        return self._acquired_as

    @acquired_as.setter
    def acquired_as(self, arg):
        assert (arg == self.filename or
                arg == self.name or
                arg == self.fullname or
                arg.endswith(self.fullname)), 'Bad arg: {0} (fullname: {1})'.format(arg, self.fullname)
        self._acquired_as = arg

    @property
    def refcount(self):
        return self._refcount

    @refcount.setter
    def refcount(self, count):
        if count < 0:
            raise ValueError('Negative reference count for {0}.  This should '
                             'never happen.  Please report this failure to '
                             'the Modulecmd.py developers'.format(self))
        self._refcount = count

    def endswith(self, string):
        return self.filename.endswith(string)

    def unlocks_dir(self, dirname):
        if dirname not in self._unlocks:
            self._unlocks.append(dirname)

    def unlocks(self, dirname):
        return dirname in self._unlocks

    def unlocked_by(self, loaded_modules):
        """Simple function which lets a module know about its dependents"""
        unlocked_by = []
        dirname = self.modulepath
        for module in loaded_modules[::-1]:
            if module.unlocks(dirname):
                unlocked_by.append(module)
                dirname = module.modulepath
        return unlocked_by[::-1]

    def read(self, mode):
        if isinstance(self, TclModule):
            if not pymod.config.has_tclsh:  # pragma: no cover
                raise TCLSHNotFoundError
            try:
                return tcl2py(self, mode)
            except Exception as e:  # pragma: no cover
                tty.die(e.args[0])
                return ''
        return open(self.filename, 'r').read()

    def prepare(self):
        self.parser = ModuleArgumentParser()

    def parse_args(self):
        return self.parser.parse_args(self.opts)

    def reset_state(self):
        self._opts = None

    @property
    def fullname(self):
        if not self.version:
            assert not self.variant
            return self.name
        elif not self.variant:
            return os.path.sep.join((self.name, self.version.string))
        return os.path.sep.join((self.name, self.version.string, self.variant.string))

    @property
    def opts(self):
        return self._opts

    @opts.setter
    def opts(self, opts):
        if opts is not None:
            self._opts = list(opts)

    def format_info(self):
        if self.is_default and self.is_loaded:
            return self.fullname + ' (D,L)'
        elif self.is_default:  # pragma: no cover
            return self.fullname + ' (D)'
        elif self.is_loaded:
            return self.fullname + ' (L)'
        return self.fullname

    def format_whatis(self):
        if not self.whatisstr:  # pragma: no cover
            return '{0}: no "whatis" description has been provided'.format(self.fullname)
        sio = StringIO()
        _, width = terminal_size()
        rule = '=' * width
        head = '{0}'.format((" " + self.name + " ").center(width, '='))
        sio.write(head + '\n')
        sio.write(fill(self.whatisstr))
        parser_help = self.parser.help_string()
        if parser_help:  # pragma: no cover
            sio.write(parser_help + '\n')
        sio.write(rule)
        return sio.getvalue()

    def set_whatis(self, *args, **kwargs):
        if isinstance(self, TclModule):
            if len(args) != 1:
                raise ValueError('unknown whatis args length for tcl module')
            self.whatisstr += args[0] + '\n'
        else:
            for arg in args:
                self.whatisstr += arg + '\n'
        for (key, value) in kwargs.items():
            key = ' '.join(key.split('_'))
            self.whatisstr += '\n' + key + ':\n'
            self.whatisstr += textfill(value, indent=2)

    def format_help(self):
        if self.helpstr is None:
            return '{0}: no help string provided'.format(self.fullname)

        sio = StringIO()
        _, width = terminal_size()
        rule = '=' * width
        head = '{0}'.format((" " + self.name + " ").center(width, '='))
        sio.write(head + '\n')
        sio.write(fill(self.helpstr))
        sio.write(rule)
        return sio.getvalue()

    def set_help_string(self,helpstr):
        self.helpstr = helpstr


class PyModule(Module):
    ext = '.py'
    def __init__(self, modulepath, *parts):
        # strip the file extension off the last part and call class initializer
        parts = list(parts)
        parts[-1], ext = os.path.splitext(parts[-1])
        assert ext == self.ext
        super(PyModule, self).__init__(modulepath, *parts)
        self.metadata = MetaData()
        self.metadata.parse(self.filename)

    @property
    def do_not_register(self):
        return self.metadata.do_not_register

    @property
    def is_enabled(self):
        return self.metadata.is_enabled

    def endswith(self, string):
        return os.path.splitext(self.filename)[0].endswith(string)


class TclModule(Module):
    pass


def module(dirname, *parts):
    filename = os.path.join(dirname, *parts)
    if not os.path.isfile(filename):  # pragma: no cover
        tty.verbose('{0} does not exist'.format(filename))
        return None
    elif filename.endswith(('~',)) or filename.startswith(('.#',)):  # pragma: no cover
        # Don't read backup files
        return None

    if filename.endswith('.py'):
        module_type = PyModule
    elif is_tcl_module(filename):
        module_type = TclModule
    else:
        return None

    module = module_type(dirname, *parts)
    if pymod.config.get('debug'):  # pragma: no cover
        if module_type == TclModule and 'gcc' in filename:
            tty.debug(module.name)
            tty.debug(module.modulepath)
            tty.debug(module.filename, '\n')

    return module


def is_tcl_module(filename):
    tcl_header = '#%Module'
    try:
        return open(filename).readline().startswith(tcl_header)
    except (IOError, UnicodeDecodeError):  # pragma: no cover
        return False


class TCLSHNotFoundError(Exception):  # pragma: no cover
    def __init__(self):
        msg = 'tclsh not found on path'
        if pymod.config.get('debug'):
            tty.die(msg)
        else:
            super(TCLSHNotFoundError, self).__init__(msg)
