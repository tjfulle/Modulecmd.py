import os
import sys
import socket
import argparse
from io import StringIO
from typing import Any, Optional

import modulecmd.xio as xio
import modulecmd.util as util
import modulecmd.environ as environ
import modulecmd._version as version
from modulecmd.util import split, isempty, ispython, ishidden


class module:
    def __init__(self, root: str, path: str) -> None:
        self.root = root
        self.path = path
        self.file = os.path.join(root, path)
        if not os.path.exists(self.file):
            raise ValueError(f"{self.file}: file not found")
        self.dirname = os.path.dirname(self.file)
        self.find_version_from_path()
        self.help_string = None
        self.short_description = None
        self.refcount = 0
        self.family = None

    def __repr__(self) -> str:
        name = self.__class__.__name__
        return f"{name}(name={self.name}, version={self.version}, root={self.root})"

    def find_version_from_path(self):
        self.fullname = os.path.splitext(self.path)[0]
        parts = self.fullname.split(os.path.sep)
        if len(parts) == 1:
            self.version = None
            self.name = self.fullname
        elif len(parts) == 2:
            self.name = parts[0]
            self.version = version.version(parts[1])
        else:
            # The fullname is name/version.  The name can have path
            # separators in it
            version_string = parts.pop()
            while parts:
                dirname = os.path.join(self.root, *parts)
                if isempty(os.path.join(dirname, ".version")):
                    self.name = os.path.sep.join(parts)
                    self.version = version.version(version_string)
                    break
                version_string = f"{parts.pop()}/{version_string}"
            else:
                self.name, version_string = os.path.split(self.fullname)
                self.version = version.version(version_string)
        return

    @staticmethod
    def valid(path: str) -> bool:
        raise NotImplementedError

    @property
    def loaded(self):
        return environ.is_loaded(self)

    @property
    def enabled(self):
        return True

    def asdict(self) -> dict:
        return {
            "file": self.file,
            "root": self.root,
            "name": self.name,
            "family": self.family,
            "opts": vars(self.opts),
            "fullname": self.fullname,
            "version": str(self.version),
        }

    def add_help(self, arg: str) -> None:
        self.help_string = arg

    def add_short_description(self, arg: str) -> None:
        self.short_description = arg

    def print_help(self):
        xio.print(self.help_string)

    def print_usage(self):
        xio.print(self.short_description)

    def load(self) -> None:
        raise NotImplementedError

    def unload(self) -> None:
        raise NotImplementedError

    def is_default(self) -> bool:
        if self.version is None:
            return False
        basename = os.path.basename(self.file)
        link = os.path.join(self.dirname, "default")
        version_file = os.path.join(self.dirname, ".version")
        if os.path.islink(link):
            return os.path.samefile(link, self.file)
        elif os.path.exists(version_file):
            default_version = util.read_tcl_default_version(version_file)
            return default_version == basename
        else:
            defaults = (".version", "default")
            members = [f for f in os.listdir(self.dirname) if f not in defaults]
            if len(members) == 1:
                return False
            versions = [version.version(os.path.splitext(_)[0]) for _ in members]
            candidates = sorted(versions)
            return candidates[-1] == self.version

    def execute(self, code, global_vars, mode):
        with environ.open(self, mode=mode):
            exec(code, global_vars, None)


class option_parser:
    def __init__(self, modulename):
        self.opts = {}
        self.modulename = modulename

    def add_option(
        self, arg: str, default: Any = None, help: str = None, type: callable = None
    ) -> None:
        type = type or str
        self.opts[arg] = {"default": default, "help": help, "type": type}

    def parse_opts(self, argv):
        opts = dict([(key, val["default"]) for (key, val) in self.opts.items()])
        for arg in argv:
            key, val = split(arg, sep="=")
            if key not in opts:
                xio.die(f"{key}: unknown module option")
            opts[key] = val
        return argparse.Namespace(**opts)

    def format_help(self) -> Optional[str]:
        if not self.opts:
            return None
        help_string = StringIO()
        help_string.write(f"{self.modulename} options\n")
        for (key, val) in self.opts.items():
            help_string.write(f"    {key}")
            if val.get("help"):
                help_string.write("     {help_string} [default: {val['default']}]")
        return help_string.getvalue()


class py_module(module):
    def __init__(self, root: str, path: str) -> None:
        super(py_module, self).__init__(root, path)
        self.enable_if = True
        self.read_meta_data()
        self.parser = option_parser(
            prefix_chars="+", prog=self.fullname, add_help=False
        )
        self.args = []

    @staticmethod
    def valid(path) -> bool:
        return ispython(path) and not ishidden(path)

    def opts(self) -> Any:
        opts = self.parser.parse_opts(self.args)
        self._opts = opts
        return opts

    def set_args(self, args: list[str]) -> None:
        if args is None:
            return
        self.args = [f"++{_}" for _ in args]

    @property
    def enabled(self) -> bool:
        return self.enable_if

    def std_exec_vars(self) -> dict[str, Any]:
        return {
            "os": os,
            "sys": sys,
            "self": self,
            "log_error": xio.die,
            "log_info": xio.info,
            "log_warn": xio.warn,
            "log_trace": xio.trace,
            "log_debug": xio.debug,
            "get_hostname": socket.gethostname,
            "help": self.add_help,
            "whatis": self.add_short_description,
            "getenv": os.getenv,
            "mkdirp": util.filesystem.mkdirp,
            "is_darwin": sys.platform == "darwin",
            "IS_DARWIN": sys.platform == "darwin",
            "load": environ.noop,
            "raw": environ.raw_shell_command,
            "source": environ.source_file,
            "family": environ.set_family,
            "setenv": environ.set_variable,
            "use": environ.use_modulepath,
            "unuse": environ.unuse_modulepath,
            "unsetenv": environ.unset_variable,
            "set_alias": environ.set_alias,
            "unset_alias": environ.unset_alias,
            "set_shell_function": environ.set_shell_function,
            "unset_shell_function": environ.unset_shell_function,
            "append_path": environ.append_path,
            "prepend_path": environ.prepend_path,
            "add_option": self.parser.add_argument,
            "opts": util.singleton(self.opts),
        }

    def print_help(self) -> None:
        xio.trace(f"Loading {self.fullname} from {self.file}")
        code = compile(open(self.file).read(), self.file, "exec")
        global_vars = self.std_exec_vars()
        global_vars["raw"] = environ.noop
        global_vars["source"] = environ.noop
        global_vars["family"] = environ.noop
        global_vars["setenv"] = environ.noop
        global_vars["unsetenv"] = environ.noop
        global_vars["set_alias"] = environ.noop
        global_vars["unset_alias"] = environ.noop
        global_vars["append_path"] = environ.noop
        global_vars["prepend_path"] = environ.noop
        self.execute(code, global_vars, "load")
        xio.print(self.format_help())

    def load(self, args: list[str] = None) -> None:
        xio.trace(f"Loading {self.fullname} from {self.file}")
        self.set_args(args)
        code = compile(open(self.file).read(), self.file, "exec")
        global_vars = self.std_exec_vars()
        self.execute(code, global_vars, "load")

    def unload(self) -> None:
        xio.trace(f"Unloading {self.fullname}")
        code = compile(open(self.file).read(), self.file, "exec")
        global_vars = self.std_exec_vars()
        global_vars["load"] = environ.noop  # unload
        global_vars["unload"] = environ.noop
        global_vars["raw"] = environ.noop
        global_vars["source"] = environ.noop
        global_vars["setenv"] = environ.unset_variable
        global_vars["set_alias"] = environ.unset_alias
        global_vars["append_path"] = environ.unappend_path
        global_vars["prepend_path"] = environ.unprepend_path
        with environ.open(self, mode="unload"):
            exec(code, global_vars, None)

    def read_meta_data(self) -> None:
        """Reads meta data
        # module: [enable_if=<bool expr>]
        """
        kwds = {}
        for line in open(self.file):
            if not line.split():
                continue
            if not line.startswith("#"):
                break
            if line.startswith(("# module:", "# pymod:")):
                directive = line.split(":", 1)[1].strip()
                key, val = util.split(directive, "=", 1)
                kwds[key] = val
        for key in ("enable_if",):
            expr = kwds.pop(key, None)
            if expr is None:
                continue
            value = util.eval_bool_expr(expr)
            if value is None:
                msg = f"{self.fullname}: {expr} is not a boolean expression"
                raise ValueError(msg)
            setattr(self, key, value)
        if len(kwds):
            msg = f"{self.fullname}: unknown meta options: {list(kwds.keys())}"
            raise ValueError(msg)

    def format_help(self):
        help_string = self.help_string
        parser_help = self.parser.format_help()
        if help_string is None and parser_help is not None:
            help_string = f"{self.fullname} module"
        if parser_help is not None:
            help_string += f"\n\n{parser_help}"
        if help_string is None:
            help_string = f"{self.fullname}: no help string provided"
        return help_string


class tcl_module(module):
    @staticmethod
    def valid(path) -> bool:
        if not os.path.isfile(path) or filesystem.ishidden(path):
            return False
        return open(path).readline().startswith("#%Module1.0")


def ishidden(path) -> bool:
    return os.path.basename(path).startswith(".")


def ismodule(path):
    if os.path.islink(path) and path.endswith("default"):
        return False
    if not os.path.isfile(path) or filesystem.ishidden(path):
        return False
    return py_module.valid(path) or tcl_module.valid(path)


def factory(root, path) -> module:
    if not ismodule(os.path.join(root, path)):
        return None
    elif path.endswith(".py"):
        return py_module(root, path)
    else:
        return tcl_module(root, path)
