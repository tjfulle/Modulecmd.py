import os
import re
import json
import stat
import zlib
import errno
import fcntl
import base64
import struct
import shutil
import termios
import textwrap
import subprocess
import importlib.util
from io import StringIO
from types import SimpleNamespace
from contextlib import contextmanager
from typing import Union, Any, Generator, Optional


def colorize(fmt: str) -> str:
    return fmt.format(
        red="\033[91m",
        green="\033[92m",
        yellow="\033[93m",
        blue="\033[94m",
        magenta="\033[95m",
        cyan="\033[96m",
        endc="\033[0m",
        bold="\033[1m",
    )


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
                return None
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
                repl = colorize("{%s}%s{endc}" % (color, item))
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
        width = terminal_size().columns
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


def pop(args: list, item: Any, from_back: bool = False) -> Any:
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


# ------------------------------------------------------------------------------------ #
# --- Filesystem helpers ------------------------------------------------------------- #
# ------------------------------------------------------------------------------------ #


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


@contextmanager
def working_dir(dirname: str) -> None:
    orig_dir = os.getcwd()
    os.chdir(dirname)
    yield
    os.chdir(orig_dir)


def which(executable, PATH=None, default=None):
    """Find path to the executable"""
    if is_executable(executable):
        return executable
    PATH = PATH or os.getenv("PATH")
    for d in split(PATH, os.pathsep):
        if not os.path.isdir(d):
            continue
        f = os.path.join(d, executable)
        if is_executable(f):
            return f
    return default


def is_executable(path):
    """Is the path executable?"""
    return os.path.isfile(path) and os.access(path, os.X_OK)


def force_symlink(src, dest):
    try:
        os.symlink(src, dest)
    except OSError:
        os.remove(dest)
        os.symlink(src, dest)


def remove_file(path: str) -> None:
    try:
        os.remove(path)
    except OSError:
        pass


def remove_directory(path: str) -> None:
    try:
        shutil.rmtree(path, ignore_errors=True)
    except OSError:
        pass


def touch(path):
    """Creates an empty file at the specified path."""
    perms = os.O_WRONLY | os.O_CREAT | os.O_NONBLOCK | os.O_NOCTTY
    fd = None
    try:
        fd = os.open(path, perms)
        os.utime(path, None)
    finally:
        if fd is not None:
            os.close(fd)


def touchp(path):
    """Like ``touch``, but creates any parent directories needed for the file."""
    mkdirp(os.path.dirname(path))
    touch(path)


def force_remove(*paths: str) -> None:
    """Remove files without printing errors.  Like ``rm -f``"""
    for path in paths:
        if not os.path.exists(path):
            continue
        elif os.path.isdir(path):
            remove_directory(path)
        else:
            remove_file(path)


def set_executable(path):
    mode = os.stat(path).st_mode
    if mode & stat.S_IRUSR:
        mode |= stat.S_IXUSR
    if mode & stat.S_IRGRP:
        mode |= stat.S_IXGRP
    if mode & stat.S_IROTH:
        mode |= stat.S_IXOTH
    os.chmod(path, mode)


# ------------------------------------------------------------------------------------ #
# --- color and colify --------------------------------------------------------------- #
# ------------------------------------------------------------------------------------ #
def clen(string: str) -> int:
    """Return the length of a string, excluding ansi color sequences."""
    return len(re.sub(r"\033[^m]*m", "", string))


def cextra(string):
    """Length of extra color characters in a string"""
    return len("".join(re.findall(r"\033[^m]*m", string)))


class column_config:
    def __init__(self, cols: int):
        self.cols: int = cols
        self.line_length: int = 0
        self.valid: bool = True
        self.widths: list[int] = [0] * cols  # does not include ansi colors

    def __repr__(self) -> str:
        attrs = [(a, getattr(self, a)) for a in dir(self) if not a.startswith("__")]
        return "<Config: %s>" % ", ".join("%s: %r" % a for a in attrs)


def config_variable_cols(elts: list[str], width: int, padding: str, cols: int = 0):
    """Variable-width column fitting algorithm.

    This function determines the most columns that can fit in the
    screen width.  Unlike uniform fitting, where all columns take
    the width of the longest element in the list, each column takes
    the width of its own longest element. This packs elements more
    efficiently on screen.

    If cols is nonzero, force

    """
    if cols < 0:
        raise ValueError("cols must be non-negative.")

    # Get a bound on the most columns we could possibly have.
    # 'clen' ignores length of ansi color sequences.
    lengths = [clen(e) for e in elts]
    max_cols = max(1, width // (min(lengths) + padding))
    max_cols = min(len(elts), max_cols)

    # Range of column counts to try.  If forced, use the supplied value.
    col_range = [cols] if cols else range(1, max_cols + 1)

    # Determine the most columns possible for the console width.
    configs = [column_config(c) for c in col_range]
    for i, length in enumerate(lengths):
        for conf in configs:
            if conf.valid:
                col = i // ((len(elts) + conf.cols - 1) // conf.cols)
                p = padding if col < (conf.cols - 1) else 0

                if conf.widths[col] < (length + p):
                    conf.line_length += length + p - conf.widths[col]
                    conf.widths[col] = length + p
                    conf.valid = conf.line_length < width

    try:
        config = next(conf for conf in reversed(configs) if conf.valid)
    except StopIteration:
        # If nothing was valid the screen was too narrow -- just use 1 col.
        config = configs[0]

    config.widths = [w for w in config.widths if w != 0]
    config.cols = len(config.widths)
    return config


def colify(elts, cols: int = 0, indent: int = 0, padding: int = 2, width: int = None):
    """Takes a list of elements as input and finds a good columnization
    of them, similar to how gnu ls does. This supports both
    uniform-width and variable-width (tighter) columns.

    If elts is not a list of strings, each element is first conveted
    using ``str()``.

    Parameters
    ----------
    indent : int
        Optionally indent all columns by some number of spaces
    padding : int
        Spaces between columns. Default is 2
    width : int
        Width of the output. Default is 80 if tty not detected

    """
    # Get keyword arguments or set defaults
    output = StringIO()
    width = width or terminal_size().columns
    width = max(1, width - indent)

    # elts needs to be an array of strings so we can count the elements
    elts = [str(elt) for elt in elts]
    if not elts:
        return output.getvalue()

    config = config_variable_cols(elts, width, padding, cols)

    cols = config.cols
    rows = (len(elts) + cols - 1) // cols
    rows_last_col = len(elts) % rows

    for row in range(rows):
        output.write(" " * indent)
        for col in range(cols):
            elt = col * rows + row
            width = config.widths[col] + cextra(elts[elt])
            if col < cols - 1:
                fmt = "%%-%ds" % width
                output.write(fmt % elts[elt])
            else:
                # Don't pad the rightmost column (sapces can wrap on
                # small teriminals if one line is overlong)
                output.write(elts[elt])

        output.write("\n")
        row += 1
        if row == rows_last_col:
            cols -= 1

    return output.getvalue().rstrip()


# ------------------------------------------------------------------------------------ #


def terminal_size():
    """Gets the dimensions of the console: (rows, cols)."""

    def ioctl_gwinsz(fd):
        try:
            rc = struct.unpack("hh", fcntl.ioctl(fd, termios.TIOCGWINSZ, "1234"))
        except BaseException:
            return
        return rc

    rc = ioctl_gwinsz(0) or ioctl_gwinsz(1) or ioctl_gwinsz(2)
    if not rc:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            rc = ioctl_gwinsz(fd)
            os.close(fd)
        except BaseException:
            pass

    if not rc:
        rc = (os.environ.get("LINES", 25), os.environ.get("COLUMNS", 80))

    return SimpleNamespace(rows=int(rc[0]) or 25, columns=int(rc[1]) or 80)


def load_module_from_file(module_name, module_path):
    """Loads a python module from the path of the corresponding file.

    Args:
        module_name (str): namespace where the python module will be loaded,
            e.g. ``foo.bar``
        module_path (str): path of the python file containing the module

    Returns:
        A valid module object

    Raises:
        ImportError: when the module can't be loaded
        FileNotFoundError: when module_path doesn't exist
    """
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
