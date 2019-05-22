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


acqby_name = 1
acqby_fullname = 2
acqby_filename = 3
acqby_path = 4
acqby_self = 5


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
        self._whatis = {}
        self._helpstr = None
        self.is_default = False
        self._opts = None
        self._unlocks = []
        self.marked_as_default = False
        self._his = None  # How the module was initially loaded

    def __str__(self):
        return 'Module(name={0})'.format(self.fullname)

    def __repr__(self):
        return 'Module(name={0})'.format(self.fullname)

    @property
    def is_loaded(self):
        lm_files = split(
            pymod.environ.get(pymod.names.loaded_module_files), os.pathsep)
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
    def his(self):
        return self._his

    @his.setter
    def his(self, arg):
        assert arg in (acqby_name, acqby_fullname,
                       acqby_filename, acqby_path, acqby_self)
        self._his = arg

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
        if 'direct set' in self._whatis:
            return '\n'.join(self._whatis['direct set'])

        sio = StringIO()
        _, width = terminal_size()
        name = self._whatis.get('name', self.name)
        head = '{0}'.format((" " + name + " ").center(width, '='))
        sio.write(head + '\n')

        sio.write('Name: {0}\n'.format(name))
        version = self._whatis.get('version', self.version.string)
        if version:
            sio.write('Version: {0}\n'.format(version))
        sio.write(
            'Family: {0}\n'
            'Full Name: {1}\n'
            'Filename: {2}\n'
            .format(self.family, self.fullname, self.filename))

        short_description = self._whatis.get('short description')
        if short_description is not None:
            key = 'Description'
            N = len(key) + 2
            ss = textfill(short_description, indent=N)
            sio.write('{0}: {1}\n'.format(key, ss))

        configure_options = self._whatis.get('configure options')
        if configure_options is not None:
            key = 'Configure Options'
            ss = '\n    '.join(configure_options.split())
            sio.write('{0}:\n    {1}\n'.format(key, ss))

        for (key, item) in self._whatis.items():
            if key in ('short description', 'configure options'):
                continue
            N = len(key) + 2
            ss = textfill(item, indent=N)
            sio.write('{0}: {1}\n'.format(key.title(), ss))

        parser_help = self.parser.help_string()
        if parser_help:  # pragma: no cover
            sio.write(parser_help + '\n')

        sio.write('=' * width)

        return sio.getvalue()

    def set_whatis(self, *args, **kwargs):
        if isinstance(self, TclModule):
            if len(args) != 1:
                raise ValueError('unknown whatis args length for tcl module')
            self._whatis['short description'] = args[0]
        else:
            for arg in args:
                self._whatis.setdefault('direct set', []).append(arg)
        for (key, value) in kwargs.items():
            key = ' '.join(key.split('_'))
            self._whatis[key] = value

    def format_help(self):
        if self._helpstr is None:
            return '{0}: no help string provided'.format(self.fullname)

        sio = StringIO()
        _, width = terminal_size()
        rule = '=' * width
        head = '{0}'.format((" " + self.name + " ").center(width, '='))
        sio.write(head + '\n')
        sio.write(fill(self._helpstr))
        sio.write(rule)
        return sio.getvalue()

    def set_help_string(self, helpstr):
        self._helpstr = helpstr


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
