from __future__ import division, print_function

import os
import re
import sys
import time
import base64
import tempfile
import subprocess
from textwrap import fill

from .color import colorize
from . import compat
from .config import cfg


execfun = compat.execfun
import_module_by_filepath = compat.import_module_by_filepath

def split(arg, sep=None, num=None):
    """Split arg on sep. Only non-empty characters are included in the returned
    list
    """
    if arg is None:
        return []
    if num is None:
        return [x.strip() for x in arg.split(sep) if x.split()]
    return [x.strip() for x in arg.split(sep, num) if x.split()]


def join(arg, sep):
    """Join arg with sep. Only non-empty characters are included in the
    returned string
    """
    return sep.join([x.strip() for x in arg if x.split()])


def join_args(*args):
    """Join args as strings"""
    return ' '.join('{0}'.format(x) for x in args)


def decode_str(x):
    """Decode the string"""
    if x is None:
        return None
    try:
        return x.decode('utf-8', 'ignore')
    except (AttributeError, TypeError):
        return x


def encode_str(string):
    try:
        return string.encode('utf-8')
    except AttributeError:
        return string


def check_output(command):
    """Implementation of subprocess's check_output"""
    import subprocess
    fh = open(os.devnull, 'a')
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=fh)
    out, err = p.communicate()
    returncode = p.poll()
    return decode_str(out)


def get_console_dims(default_rows=25, default_cols=80):
    """Return the size of the terminal"""
    out = check_output('stty size')
    try:
        rows, columns = [int(x) for x in out.split()]
    except ValueError:
        rows, columns = default_rows, default_cols
    return rows, columns


def dict2str(dikt):
    return encode2(str(dikt))


def str2dict(s):
    if s is None or not s.strip():
        return {}
    return eval(decode2(s))


def encode2(item):
    return base64.urlsafe_b64encode(str(item).encode()).decode()


def decode2(item):
    return base64.urlsafe_b64decode(str(item)).decode()


def total_module_time(initial_time):  # pragma: no cover
    t = time.time() - initial_time
    sys.stderr.write('Total time spent in modulecmd: {0:.3f} s.\n'.format(t))


def lists_are_same(a, b, key=None):
    """Are the two lists the same?"""
    if len(a) != len(b):
        return False
    if not key:
        return all([ai == b[i] for (i, ai) in enumerate(a)])
    return all([key(ai) == key(b[i]) for (i, ai) in enumerate(a)])


def grep_pat_in_string(string, pat, color='cyan'):
    regex = re.compile(pat)
    for line in string.split('\n'):
        for item in line.split():
            if regex.search(item):
                string = re.sub(re.escape(item), colorize(item, color), string)
    return string


def wrap2(list_of_str, width, numbered=0, pad='   '):
    from math import ceil, floor

    if not list_of_str:
        return ''

    num_str = len(list_of_str)
    if numbered:
        list_of_str = ['{0}{1}) {2}'.format(pad, i+1, x)
                       for i,x in enumerate(list_of_str)]
    else:
        list_of_str = [pad + x for x in list_of_str]
    col_width = max(len(x) for x in list_of_str)
    cols = int(width / col_width)
    rows = int(ceil(num_str / cols))

    array_of_str = []
    for row in range(rows):
        array_of_str.append(list_of_str[row::rows])

    return '\n'.join(''.join(x.ljust(col_width) for x in row if x is not None)
                     for row in array_of_str)


def get_unique(a):
    unique, extra = [], []
    for item in a:
        if item not in unique:
            unique.append(item)
        else:
            extra.append(item)
    return unique, extra


def is_executable(path):
    """Is the path executable?"""
    return os.path.isfile(path) and os.access(path, os.X_OK)


def which(executable, PATH=None, default=None):
    """Find path to the executable"""
    if is_executable(executable):
        return executable
    PATH = PATH or os.getenv('PATH')
    for d in split(PATH, os.pathsep):
        if not os.path.isdir(d):
            continue
        f = os.path.join(d, executable)
        if is_executable(f):
            return f
    return default


def listdir(dirname, key=None):
    if not os.path.isdir(dirname):
        items = None
    else:
        items = os.listdir(dirname)
        if key is not None:
            items = [x for x in items if key(os.path.join(dirname, x))]
    return items


def strip_quotes(item):
    """Strip beginning/ending quotations"""
    item = item.strip()
    if item[0] == '"' and item[-1] == '"':
        # strip quotations
        item = item[1:-1]
    if item[0] == "'" and item[-1] == "'":
        # strip single quotations
        item = item[1:-1]
    # SEMs uses <NAME> as an identifier, but < gets escaped, so remove
    # the escape character
    item = re.sub(r'[\\]+', '', item)
    return item


def textfill(string, width=None, indent=None, **kwds):
    if width is None:
        _, width = get_console_dims()
    if indent is not None:
        kwds['initial_indent'] = ' ' * indent
        kwds['subsequent_indent'] = ' ' * indent
    s = fill(string, width, **kwds)
    return s.lstrip()


def edit_string_in_vim(string):  # pragma: no cover
    with tempfile.NamedTemporaryFile() as tf:
        tf.write(encode_str(string+'\n'))
        tf.flush()
        subprocess.call(['vim', '-u', 'NONE', tf.name], stdout=sys.stderr)
        tf.seek(0)
        return decode_str(tf.read())


def edit_file_in_vim(filename):  # pragma: no cover
    subprocess.call(['vim', '-u', 'NONE', filename], stdout=sys.stderr)
    return None


def edit_file(filename):  # pragma: no cover
    if cfg.editor == 'vim':
        return edit_file_in_vim(filename)
    elif cfg.editor == 'user.edit_file':
        from .user import user_env
        user_env.edit_file(filename)
    else:
        subprocess.call([cfg.editor, filename], stdout=sys.stderr)


def serialize(obj, *args):  # pragma: no cover
    """JSON serializer for objects not serializable by default json code"""
    from .module2 import Module2
    if isinstance(obj, Module2):
        return obj.asdict(*args)
    raise Exception('Unknown type to serialize')


def cmp_to_key(mycmp):  # pragma: no cover
    """Convert a cmp= function into a key= function"""
    class K(object):
        def __init__(self, obj, *args):
            self.obj = obj
            def __lt__(self, other):
                return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
        def __hash__(self):
            raise TypeError('hash not implemented')
    return K
