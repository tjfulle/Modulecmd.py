import os
import re
import sys
from textwrap import fill

import pymod.config
import pymod.names
from pymod.module.meta import MetaData
from pymod.module.tcl2py import tcl2py
from pymod.module.version import Version

import contrib.util.misc as misc
import pymod.environ as environ
import contrib.util.logging as logging
from contrib.util.executable import which
from pymod.module.argument_parser import ModuleArgumentParser


has_tclsh = which('tclsh') is not None
python = 'PYTHON'
tcl = 'TCL'



# --------------------------------------------------------------------------- #
# --------------------------- MODULE CLASS ---------------------------------- #
# --------------------------------------------------------------------------- #
class Module(object):
    def __init__(self, name, fullname, version, type, path, modulepath, meta):
        self.name = name
        self.fullname = fullname
        self.version = Version(version)
        self.type = type
        self.filename = path
        self.modulepath = modulepath
        self.parser = ModuleArgumentParser()
        self.family = None
        self.short_description = None
        self.configure_options = None
        self._whatis = {}
        self._helpstr = None
        self.metadata = meta
        self.is_default = False
        self._opts = None

    def __str__(self):
        return 'Module(name={0})'.format(self.fullname)

    def __repr__(self):
        return 'Module(name={0})'.format(self.fullname)

    @property
    def is_loaded(self):
        loaded_modules = misc.split(
            environ.get(pymod.names.loaded_modules), os.pathsep)
        return self.fullname in loaded_modules

    @property
    def is_enabled(self):
        return self.metadata.is_enabled

    @property
    def is_hidden(self):
        return not self.is_enabled

    @property
    def do_not_register(self):
        return self.metadata.do_not_register

    def read(self, mode):
        if self.type == tcl:
            if not has_tclsh:
                raise TCLSHNotFoundError
            try:
                return tcl2py(self, mode)
            except Exception as e:
                logging.error(e.args[0])
                return ''
        return open(self.filename, 'r').read()

    def parse_args(self):
        return self.parser.parse_args(self.opts)

    def reset_state(self):
        self.parser = ModuleArgumentParser()

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
        elif self.is_default:
            return self.fullname + ' (D)'
        elif self.is_loaded:
            return self.fullname + ' (L)'
        return self.fullname

    def format_whatis(self):
        if 'explicit' in self._whatis:
            return '\n'.join(self._whatis['explicit'])

        s = ['Name: {0}'.format(self.name)]
        if self.version.string:
            s.append('Version: {0}'.format(self.version))
        s.extend([
            'Type: {0}'.format(self.type),
            'Family: {0}'.format(self.family),
            'Full Name: {0}'.format(self.fullname),
            'Filename: {0}'.format(self.filename), ])

        if self.short_description is not None:
            key = 'Description'
            N = len(key) + 2
            ss = misc.textfill(self.short_description, indent=N)
            s.append('{0}: {1}'.format(key, ss))

        if self.configure_options is not None:
            key = 'Configure Options'
            ss = '\n    '.join(self.configure_options.split())
            s.append('{0}:\n    {1}'.format(key, ss))

        for (key, item) in self._whatis.items():
            N = len(key) + 2
            ss = misc.textfill(item, indent=N)
            s.append('{0}: {1}'.format(key, ss))

        parser_help = self.parser.help_string()
        if parser_help:
            s.append(parser_help)

        return '\n'.join(s)

    def set_whatis(self, *args, **kwargs):
        if self.type == tcl:
            assert len(args) == 1
            kwargs['short_description'] = args[0]
        else:
            for arg in args:
                self._whatis.setdefault('explicit', []).append(arg)
        for (key, item) in kwargs.items():
            if key in ('name', 'version', 'short_description',
                       'configure_options'):
                setattr(self, key, item)
            else:
                self._whatis[' '.join(key.split('_')).title()] = item

    def format_help(self):
        if self._helpstr is None:
            return '{0!r}: no help string provided'.format(
                misc.encode_str(self.fullname))
        return fill(self._helpstr)

    def set_helpstr(self, helpstr):
        self._helpstr = helpstr


def from_file(modulepath, filepath):
    if not os.path.isfile(filepath):
        logging.verbose('{0} does not exist'.format(filepath))
        return None
    if filepath.endswith(('~',)) or filepath.startswith(('.#',)):
        # Don't read backup files
        return None

    if filepath.endswith('.py'):
        m_type = python
    elif is_tcl_module(filepath):
        m_type = tcl
    else:
        return None

    root = filepath if m_type == tcl else os.path.splitext(filepath)[0]
    fullname = root.replace(modulepath, '').lstrip(os.path.sep)
    try:
        name, version = fullname.split(os.path.sep)
    except ValueError:
        name, version = fullname, None

    meta = MetaData()
    if m_type == python:
        meta.read(filepath)

    if m_type == tcl and 'gcc' in filepath:
        logging.debug(name)
        logging.debug(modulepath)
        logging.debug(filepath, '\n')

    return Module(name, fullname, version, m_type, filepath, modulepath, meta)


def is_tcl_module(filename):
    tcl_header = '#%Module'
    try:
        return open(filename).readline().startswith(tcl_header)
    except IOError:
        return False


class TCLSHNotFoundError(Exception):
    def __init__(self):
        msg = 'tclsh not found on path'
        if pymod.config.get('debug'):
            logging.error(msg)
        else:
            super(TCLSHNotFoundError, self).__init__(msg)
