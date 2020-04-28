import os
from six import StringIO
from textwrap import fill

import pymod.mc
import pymod.config
from pymod.module.meta import MetaData
from pymod.module.tcl2py import tcl2py
from pymod.module.version import Version

from pymod.util.lang import textfill
import llnl.util.tty as tty
from llnl.util.tty import terminal_size

__all__ = ["Namespace", "Module", "PyModule", "TclModule"]


class Module(object):
    ext = None

    def __init__(self, root, path):

        self.filename = os.path.join(root, path)

        if not os.path.isfile(self.filename):
            raise IOError("{0} is not a file".format(self.filename))

        parts = path.split(os.path.sep)
        if self.ext:
            parts[-1], ext = os.path.splitext(parts[-1])
            assert ext == self.ext, "ext={0!r}!={1!r}".format(ext, self.ext)

        version = variant = None
        if len(parts) == 1:
            name = parts[0]
        elif len(parts) == 2:
            name, version = parts
        elif len(parts) == 3:
            name, version, variant = parts
        else:
            name = os.path.join(*parts)

        self.name = name
        self.version = Version(version)
        self.variant = Version(variant)

        self.modulepath = root
        self.family = None
        self.whatisstr = ""
        self.helpstr = None
        self.is_default = False
        self._unlocked_by_me = []
        self.marked_as_default = False
        self._acquired_as = None  # How the module was initially loaded
        self._refcount = 0
        self.kwargv = {}
        self.registered_options = {}

    def __str__(self):
        return "Module(name={0})".format(self.fullname)

    def __repr__(self):
        return "Module(name={0})".format(self.fullname)

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
    def acquired_as(self):
        return self._acquired_as

    @property
    def opts(self):
        return self.kwargv

    @opts.setter
    def opts(self, opts):
        self.kwargv = {} if not opts else dict(opts)

    @acquired_as.setter
    def acquired_as(self, arg):
        assert (
            arg == self.filename
            or arg == self.name
            or arg == self.fullname
            or self.endswith(arg)
        ), "Bad arg: {0} (fullname: {1})".format(arg, self.fullname)
        self._acquired_as = arg

    @property
    def refcount(self):
        return self._refcount

    @refcount.setter
    def refcount(self, count):
        if count < 0:
            raise ValueError(
                "Negative reference count for {0}.  This should "
                "never happen.  Please report this failure to "
                "the Modulecmd.py developers".format(self)
            )
        self._refcount = count

    @property
    def path(self):
        return self.filename if self.ext is None else os.path.splitext(self.filename)[0]

    def endswith(self, string):
        return len(string) > len(self.fullname) and self.path.endswith(string)

    def unlocks_path(self, path):
        """Called by the callback `use` to register which paths are unlocked
        by me.
        """
        if path not in self._unlocked_by_me:
            self._unlocked_by_me.append(path)

    def unlocks(self, path=None):
        """Return whether `path` is unlocked by this module. If `path is
        None`, then return the list of paths that are unlocked by this
        module.

        The list _unlocked_by_me is populated by the callback `use` through
        the `unlocks_path` function.
        """
        if path is None:
            return list(self._unlocked_by_me)
        return path in self._unlocked_by_me

    def unlocked_by(self):
        """Returns the module[s] that unlock this module, if any"""
        unlocks_me = []
        loaded_modules = pymod.mc.get_loaded_modules()
        dirname = self.modulepath
        for module in loaded_modules[::-1]:
            if module.unlocks(path=dirname):
                unlocks_me.append(module)
                dirname = module.modulepath
        return list(unlocks_me[::-1])

    def read(self, mode):
        raise NotImplementedError  # pragma: no cover

    def prepare(self):
        pass

    def reset_state(self):
        self.kwargv = {}

    @property
    def fullname(self):
        if not self.version:
            assert not self.variant
            return self.name
        elif not self.variant:
            return os.path.sep.join((self.name, self.version.string))
        return os.path.sep.join((self.name, self.version.string, self.variant.string))

    def format_dl_status(self):
        if self.is_default and self.is_loaded:
            return self.fullname + " (D,L)"
        elif self.is_default:  # pragma: no cover
            return self.fullname + " (D)"
        elif self.is_loaded:
            return self.fullname + " (L)"
        return self.fullname

    def format_whatis(self):
        if not self.whatisstr:  # pragma: no cover
            return '{0}: no "whatis" description has been provided'.format(
                self.fullname
            )
        sio = StringIO()
        _, width = terminal_size()
        rule = "=" * width
        head = "{0}".format((" " + self.name + " ").center(width, "="))
        text_width = min(width, 80)
        sio.write(head + "\n")
        sio.write(fill(self.whatisstr, width=text_width) + "\n")
        option_help = self.option_help_string()
        if option_help:  # pragma: no cover
            sio.write("\n" + option_help + "\n")
        sio.write(rule)
        return sio.getvalue()

    def set_whatis(self, *args, **kwargs):
        if isinstance(self, TclModule):
            if len(args) != 1:
                raise ValueError("unknown whatis args length for tcl module")
            self.whatisstr += args[0] + "\n"
        else:
            for arg in args:
                self.whatisstr += arg + "\n"
        for (key, value) in kwargs.items():
            key = " ".join(key.split("_"))
            self.whatisstr += "\n" + key + ":\n"
            self.whatisstr += textfill(value, indent=2)

    def format_help(self):
        if self.helpstr is None:
            return "{0}: no help string provided".format(self.fullname)

        sio = StringIO()
        _, width = terminal_size()
        rule = "=" * width
        head = "{0}".format((" " + self.name + " ").center(width, "="))
        sio.write(head + "\n")
        sio.write(fill(self.helpstr) + "\n")
        option_help = self.option_help_string()
        if option_help:  # pragma: no cover
            sio.write("\n" + option_help + "\n")
        sio.write(rule)
        return sio.getvalue()

    def set_help_string(self, helpstr):
        self.helpstr = helpstr

    def add_option(self, name, default=None, help=None):
        # Save for later parsing
        self.registered_options[name] = dict(default=default, help=help)

    def parse_opts(self):
        opts = Namespace()
        opts.set_defaults(**self.registered_options)

        # Set passed arguments
        unrecognized = []
        for (key, value) in self.kwargv.items():
            if key not in self.registered_options:
                unrecognized.append(key)
            else:
                opts.set(key, value)
        if unrecognized:
            tty.die(
                "{0}: unrecognized options: {1}".format(
                    self.fullname, ", ".join(unrecognized)
                )
            )

        return opts

    def option_help_string(self):
        if not self.registered_options:
            return None
        max_opt_name_length = max([len(_) for _ in self.registered_options])
        column_start = min(20, max_opt_name_length)
        help_string = StringIO()
        help_string.write("Module options:\n")
        text_width = 80 - column_start
        subsequent_indent = " " * column_start
        for (key, kwds) in self.registered_options.items():
            pad = " " * max(column_start - len(key) - 2, 2)
            line = "  {0}{1}".format(key, pad)
            this_help_str = kwds["help"]
            if this_help_str is not None:
                this_help_str = fill(
                    this_help_str, width=text_width, subsequent_indent=subsequent_indent
                )
                line += this_help_str
            help_string.write(line + "\n")
        return help_string.getvalue().rstrip()


class PyModule(Module):
    ext = ".py"

    def __init__(self, modulepath, *parts):
        # strip the file extension off the last part and call class initializer
        super(PyModule, self).__init__(modulepath, *parts)
        self.metadata = MetaData()
        self.metadata.parse(self.filename)

    @property
    def is_enabled(self):
        return self.metadata.is_enabled

    def read(self, mode):
        return open(self.filename, "r").read()

class TclModule(Module):

    def read(self, mode):
        if not pymod.config.has_tclsh:  # pragma: no cover
            raise TCLSHNotFoundError
        try:
            return tcl2py(self, mode)
        except Exception as e:  # pragma: no cover
            tty.die(e.args[0])
            return ""


class Namespace(object):
    def __init__(self, **kwds):
        for (key, val) in kwds.items():
            self.set(key, val)

    def __str__(self):  # pragma: no cover
        return "Namespace({0})".format(self.joined(", "))

    def joined(self, sep):
        return sep.join("{0}={1!r}".format(*_) for _ in self.__dict__.items())

    def set(self, key, value):
        setattr(self, key, value)

    def as_dict(self):
        return dict(self.__dict__)

    def set_defaults(self, **kwargs):
        for (key, value) in kwargs.items():
            self.set(key, value["default"])


class TCLSHNotFoundError(Exception):
    pass
