import os
import re
import sys
import fcntl
import struct
import termios
import datetime
from io import StringIO
from typing import TextIO, Any
from types import SimpleNamespace

from . import config


TRACE = 100
DEBUG = 80
INFO = 60
WARN = 40
ERROR = 20
DEFAULT_LOG_LEVEL = INFO
LOG_LEVEL = DEFAULT_LOG_LEVEL

error_stream = sys.stderr
output_stream = sys.stderr


def set_log_level(log_level: int) -> None:
    global LOG_LEVEL
    assert log_level in (TRACE, DEBUG, INFO, WARN, ERROR)
    LOG_LEVEL = log_level


def get_log_level_by_name(name: str) -> None:
    mapping: dict[str, int] = {
        "trace": TRACE,
        "debug": DEBUG,
        "info": INFO,
        "warn": WARN,
        "error": ERROR,
    }
    return mapping[name.lower()]


def set_output_stream(stream: TextIO) -> None:
    global output_stream
    output_stream = stream


def set_log_level_by_name(name: str) -> None:
    set_log_level(get_log_level_by_name(name))


def print(message: str, end: str = "\n", file: TextIO = None) -> None:
    file = file or output_stream
    file.write(f"{message}{end}")


def cprint(fmt: str, end: str = "\n", file: TextIO = None) -> None:
    message = colorize(fmt)
    file = file or output_stream
    file.write(f"{message}{end}")


def timestamp() -> str:
    now = datetime.datetime.now()
    return now.strftime("%Y.%m.%d %H:%M:%S")


def trace(message: str, end: str = "\n") -> None:
    if LOG_LEVEL >= TRACE:
        cprint("{bold}{yellow}==>{endc} [%s] %s" % (timestamp(), message), end=end)


def debug(message: str, end: str = "\n") -> None:
    if LOG_LEVEL >= TRACE:
        cprint("{bold}{green}==>{endc} [%s] %s" % (timestamp(), message), end=end)


def info(message: str, end: str = "\n") -> None:
    if LOG_LEVEL >= INFO:
        cprint("{bold}{blue}==>{endc} %s" % message, end=end)


def warn(message: str, end: str = "\n") -> None:
    if LOG_LEVEL >= WARN:
        fmt = "{bold}{magenta}==>{endc} Warning: %s" % message
        cprint(fmt, end=end, file=error_stream)


def error(message: str, end: str = "\n") -> None:
    if LOG_LEVEL >= ERROR:
        fmt = "{bold}{red}==>{endc} Error: %s" % message
        cprint(fmt, end=end, file=error_stream)
        if config.get("debug"):
            raise ValueError(message)


def die(message: str, end: str = "\n", code=1) -> None:
    error(message, end=end)
    sys.exit(code)


def clen(string: str) -> int:
    """Return the length of a string, excluding ansi color sequences."""
    return len(re.sub(r"\033[^m]*m", "", string))


def cextra(string):
    """Length of extra color characters in a string"""
    return len("".join(re.findall(r"\033[^m]*m", string)))


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


def pager(text: str, plain: bool = False) -> Any:  # pragma: no cover
    if plain:
        pager = plainpager
    elif sys.version_info[0] == 2:
        pager = plainpager
    elif hasattr(sys, "_pytest_in_progress_"):
        pager = plainpager
    elif hasattr(os, "system") and os.system("(less) 2>/dev/null") == 0:
        pager = pipepager  # lambda text: pipepager(text, '>&2 less')
    else:
        pager = plainpager
    pager(text)


def plainpager(text: str) -> None:  # pragma: no cover
    encoding = getattr(sys.stderr, "encoding", None) or "utf-8"
    string = text.encode(encoding, "backslashreplace").decode(encoding)
    sys.stderr.write(string)


def pipepager(text: str) -> Any:  # , cmd):  # pragma: no cover
    """Page through text by feeding it to another program."""
    cmd = ">&2 less -R"
    import io
    import subprocess

    proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE)
    try:
        with io.TextIOWrapper(proc.stdin, errors="backslashreplace") as pipe:
            try:
                pipe.write(text)
            except KeyboardInterrupt:
                # We've hereby abandoned whatever text hasn't been written,
                # but the pager is still in control of the terminal.
                pass
    except OSError:
        pass  # Ignore broken pipes caused by quitting the pager program.
    while True:
        try:
            proc.wait()
            break
        except KeyboardInterrupt:
            # Ignore ctl-c like the pager itself does.  Otherwise the pager is
            # left running and the terminal is in raw mode and unusable.
            pass
