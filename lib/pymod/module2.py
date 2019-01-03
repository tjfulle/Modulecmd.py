import os
import re
import sys
from textwrap import fill
import platform

from .constants import *
from .cfg import cfg
from .trace import trace
from .tcl2py import tcl2py
from .logging import logging
from .utils import which, split
from .optparse import ModuleOptionParser


has_tclsh = which('tclsh') is not None


class TCLModulesNotFoundError(Exception):
    def __init__(self):
        msg = 'TCL modules not installed'
        if cfg.verbosity < 2:
            logging.error(msg)
        else:
            super(TCLModulesNotFoundError, self).__init__(msg)


def read_metadata(filename):
    regex = re.compile(r'#\s*pymod\:')
    head = open(filename).readline()
    if not regex.search(head):
        return None
    pymod_directive = split(regex.split(head, 1)[1], ',')
    metadata = dict([split(x, '=', 1) for x in pymod_directive])
    bool_options = ('enable_if', 'do_not_register')
    for (key, val) in metadata.items():
        try:
            val = eval(val)
        except:
            if key in bool_options:
                logging.error('Failed to evaluate meta data '
                              'statement {0!r} in {1!r}'.format(val, filename))
        if key in bool_options and not isinstance(val, bool):
            logging.error('{0} statement in {1!r} must '
                          'evaluate to a bool'.format(key, filename))
        metadata[key] = val
    return metadata


def create_module_from_file(modulepath, path, is_explicit_default):
    if not os.path.isfile(path):
        logging.warning('{0} does not exist'.format(path), minverbosity=2)
        return None
    dirname, f = os.path.split(path)
    if f.endswith('~'):
        # Don't backup files
        return None
    if f.endswith('.py'):
        m_type = M_PY
    else:
        # If it is not python, it must be TCL
        tcl_header = '#%Module'
        try:
            tcl_module = open(path).readline().startswith(tcl_header)
        except IOError:
            return None
        else:
            if not tcl_module:
                return None
        m_type = M_TCL

    root = path if m_type == M_TCL else os.path.splitext(path)[0]
    fullname = root.replace(modulepath, '').lstrip(os.path.sep)
    try:
        name, version = fullname.split(os.path.sep)
    except ValueError:
        name, version = fullname, None

    meta = None if m_type != M_PY else read_metadata(path)

    if m_type == M_TCL and 'gcc' in path:
        logging.debug(name)
        logging.debug(modulepath)
        logging.debug(path, '\n')

    return Module2(name, fullname, version, m_type, path, modulepath,
                   is_explicit_default, meta=meta)


def create_module_from_kwds(**kwds):
    name = kwds['name']
    version = kwds['version']
    m_type = kwds['type']

    fullname = kwds.get('fullname')
    if fullname is None:
        if version is None:
            fullname = name
        else:
            fullname = os.path.join(name, version)

    is_explicit_default = kwds.get('is_explicit_default')
    if is_explicit_default is None:
        is_explicit_default = bool(kwds.get('is_default'))

    return Module2(name, fullname, version, m_type,
                   kwds['filename'], kwds['modulepath'], is_explicit_default,
                   meta=kwds.get('metadata'), data=kwds.get('data'))


# --------------------------------------------------------------------------- #
# --------------------------- MODULE CLASS ---------------------------------- #
# --------------------------------------------------------------------------- #
class Module2(object):
    def __init__(self, name, fullname, version, type, path, modulepath,
                 is_explicit_default, meta=None, data=None):
        self.name = name
        self.fullname = fullname
        self.version = version
        self.type = type
        self.filename = path
        self.modulepath = modulepath
        self.is_explicit_default = is_explicit_default
        self.is_default = None
        self.is_loaded = False
        self.options = ModuleOptionParser()
        self.family = None
        self.short_description = None
        self.configure_options = None
        self._whatis ={}
        self._helpstr = None
        self.metadata = meta
        self.version_tuple = self.get_version_tuple()
        self._data = data

    def __str__(self):
        return 'Module2(name={0})'.format(self.fullname)

    def __repr__(self):
        return 'Module2(name={0})'.format(self.fullname)

    def reset_default_status(self):
        self.is_default = None

    @property
    def is_enabled(self):
        if not self.metadata:
            return True
        return self.metadata.get('enable_if', True)

    @property
    def is_hidden(self):
        return not self.is_enabled

    @property
    def do_not_register(self):
        if not self.metadata:
            return False
        return self.metadata.get('do_not_register', False)

    @trace
    def asdict(self, *args):
        d = dict(name=self.name, fullname=self.fullname, version=self.version,
                 type=self.type, filename=self.filename, modulepath=self.modulepath,
                 is_explicit_default=self.is_explicit_default,
                 metadata=self.metadata)
        if args:
            mode, env = args
            d['data'] = self.data(mode, env)
        return d

    def data(self, mode, env):
        if self._data is not None:
            return self._data
        if self.type == M_TCL:
            if not has_tclsh:
                raise TCLModulesNotFoundError
            try:
                return tcl2py(self, mode, env)
            except Exception as e:
                logging.error(e.args[0])
                return ''
        return open(self.filename, 'r').read()

    def deactivate(self):
        self.is_default = False
        self.is_loaded = False

    def reset_state(self):
        self.options = ModuleOptionParser()

    def add_option(self, option, action='store_true', help=None):
        return self.options.add_option(option, action=action, help=help)

    def add_mutually_exclusive_option(self, o1, o2, action='store_true',
                                      help=None):
        return self.options.add_mutually_exclusive_option(
            o1, o2, action=action, help=help)

    def parse_opts(self, argv):
        ns = self.options.parse_opts(argv)
        return ns

    def get_set_options(self):
        return self.options.get_set_options()

    @staticmethod
    def _split_version_string(v):
        def Int(i):
            try: return int(i)
            except: return i
        ver_tup = [Int(x) for x in re.split(r'[-.]', v) if x.split()]
        return ver_tup

    def version_is_greater(self, other):
        if self.version is None:
            return False
        if other.version is None:
            return True
        try:
            my_ver_tup = self._split_version_string(self.version)
            other_ver_tup = self._split_version_string(other.version)
            m = min(len(my_ver_tup), len(other_ver_tup))
            return my_ver_tup[:m] > other_ver_tup[:m]
        except TypeError:
            return self.version > other.version

    def get_version_tuple(self):
        v = self.version
        if v is None:
            return None
        def _int(i):
            try: return int(i)
            except: return i
        v2 = []
        for x in v.split('.'):
            if re.search('[-_]', x):
                x = re.split('[-_]', x)
                v2.extend(x)
            else:
                v2.append(x)
        return tuple([_int(x) for x in v2])

    def describe2(self):
        if self.is_default and self.is_loaded:
            return self.fullname + ' (D,L)'
        elif self.is_default:
            return self.fullname + ' (D)'
        elif self.is_loaded:
            return self.fullname + ' (L)'
        return self.fullname

    def describe(self):
        return self.describe2()

    @property
    def whatis(self):
        if 'explicit' in self._whatis:
            return '\n'.join(self._whatis['explicit'])

        s = ['Name: {0}'.format(self.name),
             'Version: {0}'.format(self.version),
             'Type: {0}'.format(self.type),
             'Family: {0}'.format(self.family),
             'Full Name: {0}'.format(self.fullname),
             'Filename: {0}'.format(self.filename), ]

        if self.short_description is not None:
            key = 'Description'
            N = len(key) + 2
            ss = textfill(self.short_description, indent=N)
            s.append('{0}: {1}'.format(key, ss))

        if self.configure_options is not None:
            key = 'Configure Options'
            ss = '\n    '.join(self.configure_options.split())
            s.append('{0}:\n    {1}'.format(key, ss))

        for (key, item) in self._whatis.items():
            N = len(key) + 2
            ss = textfill(item, indent=N)
            s.append('{0}: {1}'.format(key, ss))

        if self.options.registered_options:
            s.append(self.options.description())

        return '\n'.join(s)

    def set_whatis(self, *args, **kwargs):
        if self.type == M_TCL:
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

    @property
    def helpstr(self):
        if self._helpstr is None:
            return '{0!r}: no help string provided'.format(
                encode_str(self.fullname))
        return fill(self._helpstr)

    @helpstr.setter
    def helpstr(self, helpstr):
        self._helpstr = helpstr
