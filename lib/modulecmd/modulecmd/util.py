import os
import re
import json
import zlib
import errno
import base64
import textwrap
import subprocess
from contextlib import contextmanager
from typing import Union, Any, Generator, Optional

import modulecmd.xio as xio


def unique(a: list[Any]) -> Generator[Any, None, None]:
    unique_items = set()
    for item in a:
        if item not in unique_items:
            yield item
            unique_items.add(item)


def safe_int(a: str) -> int:
    try:
        return int(float(a))
    except ValueError:
        return a


def split(
    arg: Union[str, None],
    sep: str = None,
    maxsplit: int = -1,
    transform: callable = None,
) -> list[Any]:
    if not arg:
        return []
    parts: list[str] = [
        _.strip() for _ in arg.split(sep, maxsplit=maxsplit) if _.split()
    ]
    if transform is None:
        return parts
    return [transform(_) for _ in parts]


def join(arg: list[Any], sep: str = None, string: callable = str) -> str:
    if not arg:
        return ""
    if sep is None:
        sep = " "
    return sep.join(string(_) for _ in arg)


class singleton:
    """Simple wrapper for lazily initialized singleton objects."""

    def __init__(self, factory: callable) -> None:
        """Create a new singleton to be initiated with the factory function.

        Args:
            factory (function): function taking no arguments that
                creates the singleton instance.
        """
        self.factory: callable = factory
        self._instance: Any = None

    @property
    def instance(self) -> Any:
        if self._instance is None:
            self._instance = self.factory()
        return self._instance

    def __getattr__(self, name: str) -> Any:
        # When unpickling Singleton objects, the 'instance' attribute may be
        # requested but not yet set. The final 'getattr' line here requires
        # 'instance'/'_instance' to be defined or it will enter an infinite
        # loop, so protect against that here.
        if name in ["_instance", "instance"]:
            raise AttributeError()
        return getattr(self.instance, name)

    def __getitem__(self, name: str) -> Any:
        return self.instance[name]

    def __contains__(self, element: Any) -> Any:
        return element in self.instance

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.instance(*args, **kwargs)

    def __iter__(self) -> Any:
        return iter(self.instance)

    def __str__(self) -> str:
        return str(self.instance)

    def __repr__(self) -> str:
        return repr(self.instance)


def deserialize(serialized: Union[str, list]) -> Any:
    if isinstance(serialized, list):
        serialized = "".join(serialized)
    string = _decode(serialized)
    return json.loads(string)


def serialize(obj: Any, chunk_size: int = None) -> list[str]:
    serialized = _encode(json.dumps(obj))
    if chunk_size is None:
        return serialized
    elif chunk_size < 0:
        return [serialized]
    return textwrap.wrap(serialized, chunk_size)


def _encode(item, compress: bool = True) -> str:
    encoded = str(item).encode("utf-8")
    if compress:
        encoded = zlib.compress(encoded)
    return base64.urlsafe_b64encode(encoded).decode()


def _decode(item, compress: bool = True) -> str:
    encoded = base64.urlsafe_b64decode(str(item))
    if compress:
        encoded = zlib.decompress(encoded)
    return encoded.decode()


def envbool(name: str) -> bool:
    if name not in os.environ:
        return False
    elif os.environ[name].lower() in ("1", "true", "yes", "on"):
        return True
    return False


def read_tcl_default_version(filename: str) -> Optional[str]:
    with open(filename) as fh:
        for (i, line) in enumerate(fh.readlines()):
            line = " ".join(line.split())
            if i == 0 and not line.startswith("#%Module"):
                xio.debug("version file does not have #%Module header")
            if line.startswith("set ModulesVersion"):
                raw_version = line.split("#", 1)[0].split()[-1]
                try:
                    version = eval(raw_version)
                except (SyntaxError, NameError):
                    version = raw_version
                return version
    return None


def eval_bool_expr(expr: str) -> Optional[bool]:
    import os, sys  # noqa: F401,E401

    # The above inserts aren't used locally, but might be in the eval below
    try:
        return bool(eval(expr))
    except:  # noqa: E722
        return None


def grep_pat_in_string(string: str, pat: str, color: str = "cyan") -> str:
    regex = re.compile(pat)
    for line in string.split("\n"):
        for item in line.split():
            if regex.search(item):
                repl = xio.colorize("{%s}%s{endc}" % (color, item))
                string = re.sub(re.escape(item), repl, string)
    return string

def boolean(item) -> Optional[bool]:
    if item is None:
        return None
    elif isinstance(item, str):
        return True if item.upper() in ("TRUE", "ON", "1") else False
    return bool(item)


def textfill(string, width=None, indent=None, **kwds):
    if width is None:
        width = xio.terminal_size().columns
    if indent is not None:
        kwds["initial_indent"] = " " * indent
        kwds["subsequent_indent"] = " " * indent
    s = textwrap.fill(string, width, **kwds)
    return s


def get_system_manpath() -> Optional[str]:
    for file in ("/usr/bin/manpath", "/bin/manpath"):
        if os.path.isfile(file):
            break
    else:  # pragma: no cover
        return None
    env = os.environ.copy()
    env.pop("MANPATH", None)
    env["PATH"] = "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/X11/bin"
    output = subprocess.check_output(file, env=env)
    return output.strip()


class filesystem:
    @staticmethod
    def isreadable(path: str, validator: callable = os.path.exists) -> bool:
        return validator(path) and os.access(path, os.R_OK)

    @staticmethod
    def isempty(path: str) -> bool:
        try:
            return os.path.getsize(path) == 0
        except OSError:
            return False

    @staticmethod
    def ispython(path: str) -> bool:
        return os.path.isfile(path) and path.endswith(".py")

    @staticmethod
    def ishidden(path: str) -> bool:
        return os.path.basename(path).startswith(".")

    @staticmethod
    @contextmanager
    def working_dir(dirname: str) -> None:
        orig_dir = os.getcwd()
        os.chdir(dirname)
        yield
        os.chdir(orig_dir)

    @staticmethod
    def mkdirp(path: str, mode: int = None) -> None:
        """Creates a directory, as well as parent directories if needed.

        Arguments:
            path (str): path to create

        Keyword Aguments:
            mode (permission bits or None, optional): optional permissions to
                set on the created directory -- use OS default if not provided
        """
        if not os.path.exists(path):
            try:
                os.makedirs(path)
                if mode is not None:
                    os.chmod(path, mode)
            except OSError as e:
                if e.errno != errno.EEXIST or not os.path.isdir(path):
                    raise e
        elif not os.path.isdir(path):
            raise OSError(errno.EEXIST, "File already exists", path)

    @staticmethod
    def which(executable, PATH=None, default=None):
        """Find path to the executable"""
        if filesystem.is_executable(executable):
            return executable
        PATH = PATH or os.getenv("PATH")
        for d in split(PATH, os.pathsep):
            if not os.path.isdir(d):
                continue
            f = os.path.join(d, executable)
            if filesystem.is_executable(f):
                return f
        return default

    @staticmethod
    def is_executable(path):
        """Is the path executable?"""
        return os.path.isfile(path) and os.access(path, os.X_OK)


def pop(args: list, item: Any, from_back: bool=False) -> Any:
    if item in args:
        if from_back:
            i = -(args[::-1].index(item)) - 1
        else:
            i = args.index(item)
        return args.pop(i)


def groupby(iterable: Any, key: Any) -> dict:
    grouped = {}
    for item in iterable:
        grouped.setdefault(key(item), []).append(item)
    return grouped.items()
