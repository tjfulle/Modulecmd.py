import os
import re
import base64
import textwrap
import subprocess
from llnl.util.tty import terminal_size

__all__ = [
    'split', 'join', 'join_args', 'decode_str', 'encode_str',
    'dict2str', 'str2dict', 'encode64', 'decode64', 'boolean',
    'pop', 'strip_quotes', 'check_output', 'which', 'is_executable',
    'textfill', 'listdir']


def listdir(dirname, key=None):
    items = os.listdir(dirname)
    if key is None:
        return items
    return [x for x in items if key(os.path.join(dirname, x))]


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


def dict2str(dikt):
    if not isinstance(dikt, (dict,)):
        raise ValueError('Expected dict')
    return encode64(str(dikt))


def str2dict(s):
    if s is None or not s.strip():
        return {}
    return eval(decode64(s))


def encode64(item):
    return base64.urlsafe_b64encode(str(item).encode()).decode()


def decode64(item):
    return base64.urlsafe_b64decode(str(item)).decode()


def boolean(item):
    if item is None:
        return None
    return True if item.upper() in ('TRUE', 'ON', '1') else False


def pop(list, item, from_back=False):
    if item in list:
        if from_back:
            i = -(list[::-1].index(item)) - 1
        else:
            i = list.index(item)
        list.pop(i)


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


def check_output(command):
    """Implementation of subprocess's check_output"""
    import subprocess
    fh = open(os.devnull, 'a')
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=fh)
    out, err = p.communicate()
    returncode = p.poll()
    return decode_str(out)


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


def is_executable(path):
    """Is the path executable?"""
    return os.path.isfile(path) and os.access(path, os.X_OK)


def textfill(string, width=None, indent=None, **kwds):
    if width is None:
        _, width = terminal_size()
    if indent is not None:
        kwds['initial_indent'] = ' ' * indent
        kwds['subsequent_indent'] = ' ' * indent
    s = textwrap.fill(string, width, **kwds)
    return s.lstrip()
