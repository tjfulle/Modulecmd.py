import os
import sys


def pager(text, plain=False):  # pragma: no cover
    if plain:
        pager = plainpager
    elif sys.version_info[0] == 2:
        pager = plainpager
    elif hasattr(sys, '_pytest_in_progress_'):
        pager = plainpager
    elif hasattr(os, 'system') and os.system('(less) 2>/dev/null') == 0:
        pager = pipepager  # lambda text: pipepager(text, '>&2 less')
    else:
        pager = plainpager
    pager(text)


def plainpager(text):  # pragma: no cover
    encoding = getattr(sys.stderr, 'encoding', None) or 'utf-8'
    string = text.encode(encoding, 'backslashreplace').decode(encoding)
    sys.stderr.write(string)


def pipepager(text):  # , cmd):  # pragma: no cover
    """Page through text by feeding it to another program."""
    cmd = '>&2 less -R'
    import io
    import subprocess
    proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE)
    try:
        with io.TextIOWrapper(proc.stdin, errors='backslashreplace') as pipe:
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
