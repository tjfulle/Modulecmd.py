import os
from six import StringIO
from textwrap import fill

import pymod.config
from pymod.module.meta import MetaData
from pymod.module.tcl2py import tcl2py
from pymod.module.version import Version

from contrib.util import textfill
import llnl.util.tty as tty
from llnl.util.tty import terminal_size

__all__ = ['Namespace', 'Module', 'PyModule', 'TclModule']


# --------------------------------------------------------------------------- #
# --------------------------- MODULE CLASS ---------------------------------- #
# --------------------------------------------------------------------------- #
class Module(object):
    ext = None
    def __init__(self, modulepath, *parts):
        self.parts = list(parts)
        self.filename = os.path.join(modulepath, *parts)

        if not os.path.isfile(self.filename):
            raise IOError('{0} is not a file'.format(self.filename))

        parts = list(parts)
        if self.ext:
            parts[-1], ext = os.path.splitext(parts[-1])
            assert ext == self.ext, 'ext={0!r}!={1!r}'.format(ext, self.ext)
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
        self.family = None
        self.whatisstr = ''
        self.helpstr = None
        self.is_default = False
        self._opts = Namespace()
        self._unlocks = []
        self.marked_as_default = False
        self._acquired_as = None  # How the module was initially loaded
        self._refcount = 0
        self.registered_options = {}

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
        raise NotImplementedError # pragma: no cover

    def prepare(self):
        pass

    def reset_state(self):
        self._opts = Namespace()

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
        if not opts:
            self._opts = Namespace()
        else:
            for (key, val) in opts.items():
                self._opts.set(key, val)

    def add_option(self, name, **kwargs):
        self.registered_options[name] = dict(kwargs)
        if name not in self._opts:
            self._opts.set(name, kwargs.get('default', None))

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
        text_width = min(width, 80)
        sio.write(head + '\n')
        sio.write(fill(self.whatisstr, width=text_width)+'\n')
        option_help = self.option_help_string()
        if option_help:  # pragma: no cover
            sio.write('\n' + option_help + '\n')
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
        sio.write(fill(self.helpstr)+'\n')
        option_help = self.option_help_string()
        if option_help:  # pragma: no cover
            sio.write('\n' + option_help + '\n')
        sio.write(rule)
        return sio.getvalue()

    def set_help_string(self, helpstr):
        self.helpstr = helpstr

    def option_help_string(self):
        if not self.registered_options:
            return None
        max_opt_name_length = max([len(_) for _ in self.registered_options])
        column_start = min(20, max_opt_name_length)
        help_string = StringIO()
        help_string.write('Module options:\n')
        text_width = 80 - column_start
        subsequent_indent = ' ' * column_start
        for (key, kwds) in self.registered_options.items():
            pad = ' ' * max(column_start - len(key) - 2, 2)
            line = '  {0}{1}'.format(key, pad)
            this_help_str = kwds.get('help')
            if this_help_str is not None:
                this_help_str = fill(this_help_str, width=text_width,
                                     subsequent_indent=subsequent_indent)
                line += this_help_str
            help_string.write(line+'\n')
        return help_string.getvalue().rstrip()


class PyModule(Module):
    ext = '.py'
    def __init__(self, modulepath, *parts):
        # strip the file extension off the last part and call class initializer
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

    def read(self, mode):
        return open(self.filename, 'r').read()


class TclModule(Module):
    def read(self, mode):
        if not pymod.config.has_tclsh:  # pragma: no cover
            raise TCLSHNotFoundError
        try:
            return tcl2py(self, mode)
        except Exception as e:  # pragma: no cover
            tty.die(e.args[0])
            return ''


class Namespace(object):
    def __init__(self, **kwds):
        for (key, val) in kwds.items():
            self.set(key, val)
    def __bool__(self):
        return any([v is not None for k,v in self.__dict__.items()])
    def __str__(self):  # pragma: no cover
        return 'Namespace({0})'.format(self.joined(', '))
    def __contains__(self, key):
        return hasattr(self, key)
    def joined(self, sep):
        return sep.join('{0}={1!r}'.format(*_) for _ in self.__dict__.items())
    def items(self):
        return self.__dict__.items()
    def set(self, key, value):
        setattr(self, key, value)
    def as_dict(self):
        return dict(self.__dict__)
