import os
import sys
from functools import wraps
from typing import Any, Optional

from . import config
from . import environ
from . import xio

_shell = None


def get_shell():
    if _shell is None:
        sh = default_shell_type()
        set_shell(sh)
    return _shell


def default_shell_type() -> Optional[str]:
    shell = os.getenv("SHELL")
    if shell is None:
        raise ValueError("Unable to determine shell from environment")
    return shell_type(os.path.basename(shell))


def shell_type(arg: str):
    if arg in ("bash", "sh", "shell.posix"):
        return "shell.posix"
    elif arg in ("csh", "tcsh", "shell.csh"):
        return "shell.csh"
    else:
        raise ValueError(f"{arg!r}: invalid shell")


def set_shell(arg: str) -> None:
    global _shell
    _shell = shell_type(arg)


def modifies_shell_environment(fun: callable) -> callable:
    xio.set_output_stream(sys.stderr)

    @wraps(fun)
    def inner(*args: Any, **kwargs: Any) -> Any:
        out = fun(*args, **kwargs)
        apply_environment_modifications()
        return out

    return inner


def apply_environment_modifications() -> None:
    shell = get_shell()
    if shell == "shell.posix":
        posix.apply_environment_modifcations()
    else:
        raise NotImplementedError(f"apply_environment_modifcations for {shell} shell")


class posix:
    @staticmethod
    def apply_environment_modifcations() -> None:
        dryrun = config.get("dryrun")
        file = sys.stderr if dryrun else sys.stdout
        for (var, value) in environ.variables():
            if value is None:
                xio.print(f"unset {var};", file=file)
            else:
                xio.print(f'export {var}="{value}"; export {var};', file=file)
        for (name, body) in environ.aliases():
            if body is None:
                xio.print(f"unalias {name} 2> /dev/null || true;", file=file)
            else:
                xio.print(f"alias {name}={body!r};", file=file)
        for (name, body) in environ.shell_functions():
            if body is None:
                xio.print(f"unset -f {name} 2> /dev/null || true;", file=file)
            else:
                xio.print(f"{name}() {{ {body.rstrip(';')}; }};", file=file)
        for filename in environ.files_to_source():
            xio.print(f"source {filename};", file=file)
        for command in environ.raw_shell_commands():
            xio.print(f"{command};", file=file)
