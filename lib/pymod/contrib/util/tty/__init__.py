import sys
from contextlib import contextmanager

from contrib.util.tty.pager import pager
from contrib.util.tty.grep import grep_pat_in_string

@contextmanager
def redirect_stdout(stdout=sys.stderr):
    old_stdout = sys.stdout
    sys.stdout = stdout
    yield
    sys.stdout = old_stdout
