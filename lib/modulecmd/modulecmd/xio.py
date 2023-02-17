import os
import sys
import datetime
from typing import TextIO, Any

import modulecmd.util as util
import modulecmd.config as config


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
    message = util.colorize(fmt)
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
