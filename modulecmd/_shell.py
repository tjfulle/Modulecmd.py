import os
import re
import sys
from io import StringIO
from functools import wraps
from typing import Any, Optional, TextIO

import modulecmd.xio as xio
import modulecmd.config as config
import modulecmd.environ as environ
import modulecmd.system as system

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
    file = StringIO()
    if shell == "shell.posix":
        posix.print_environment_modifcations(file=file)
    elif shell == "shell.csh":
        csh.print_environment_modifcations(file=file)
    else:
        raise NotImplementedError(f"apply_environment_modifcations for {shell} shell")
    dest = environ.destination_dir()
    if dest is not None:
        file.write(f"cd {dest};\n")
    text = file.getvalue()
    dryrun = config.get("dryrun")
    xio.print(text.rstrip(), file=sys.stderr if dryrun else sys.stdout)

    file = StringIO()
    system.print_changes(file=file)
    text = file.getvalue()
    if text.split():
        xio.print(text.rstrip())


class posix:
    @staticmethod
    def print_environment_modifcations(file: TextIO = None) -> None:
        file = file or sys.stdout
        for (var, value) in environ.variables():
            if value is None:
                file.write(f"unset {var};\n")
            else:
                file.write(f'export {var}="{value}"; export {var};\n')
        for (name, body) in environ.aliases():
            if body is None:
                file.write(f"unalias {name} 2> /dev/null || true;\n")
            else:
                file.write(f"alias {name}={body!r};\n")
        for (name, body) in environ.shell_functions():
            if body is None:
                file.write(f"unset -f {name} 2> /dev/null || true;\n")
            else:
                file.write(f"{name}() {{ {body.rstrip(';')}; }};\n")
        for filename in environ.files_to_source():
            file.write(f"source {filename};\n")
        for command in environ.raw_shell_commands():
            file.write(f"{command};\n")


class csh:
    limit = 4000

    @staticmethod
    def print_environment_modifcations(file: TextIO = None) -> None:
        file = file or sys.stdout
        for (var, value) in environ.variables():
            if value is None:
                file.write(f"unsetenv {var};\n")
            else:
                # csh barfs on long env vars
                if len(value) > csh.limit:
                    if var == "PATH":
                        value = csh.truncate_path(value)
                    else:
                        msg = f"{var} exceeds {csh.limit} characters, truncating..."
                        xio.warn(msg)
                        value = value[: csh.limit]
            file.write(f'setenv {var} "{value}";\n')
        aliases = dict(environ.aliases)
        aliases.update(environ.shell_function())
        for (name, body) in aliases.items():
            if body is None:
                file.write(f"unalias {name} 2> /dev/null || true;\n")
            else:
                body = body.rstrip(";")
                # Convert $n -> \!:n
                body = re.sub(r"\$([0-9]+)", r"\!:\1", body)
                # Convert $* -> \!*
                body = re.sub(r"\$\*", r"\!*", body)
                file.write(f"alias {name} '{body}';\n")
        for filename in environ.files_to_source():
            file.write(f"source {filename};\n")
        for command in environ.raw_shell_commands():
            file.write(f"{command};\n")

    def truncate_path(path):
        xio.warn(f"Truncating PATH because it exceeds {csh.limit} characters")
        truncated = ["/usr/bin", "/bin"]
        length = len(truncated[0]) + len(truncated[1]) + 1
        for (i, item) in enumerate(path.split(os.pathsep)):
            if (len(item) + 1 + length) > csh.limit:
                break
            else:
                length += len(item) + 1
                truncated.insert(-2, item)
        return os.pathsep.join(truncated)


class python:
    @staticmethod
    def print_environment_modifcations(file: TextIO = None) -> None:
        file = file or sys.stdout
        for (var, value) in environ.variables():
            if value is None:
                file.write(f"del os.environ[{var!r}]\n")
            else:
                file.write(f"os.environ[{var!r}] = {value!r}")
        for (name, body) in environ.aliases():
            file.write(f"alias_{name} = {body!r}")
        for (name, body) in environ.shell_functions():
            file.write(f"shell_function_{name} = {body!r}")
