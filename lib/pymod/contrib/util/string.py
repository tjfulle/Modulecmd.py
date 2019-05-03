import os
import re
import base64

from contrib.util.logging.color import colorize


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
    return encode64(str(dikt))


def str2dict(s):
    if s is None or not s.strip():
        return {}
    return eval(decode64(s))


def encode64(item):
    return base64.urlsafe_b64encode(str(item).encode()).decode()


def decode64(item):
    return base64.urlsafe_b64decode(str(item)).decode()


def grep_pat_in_string(string, pat, color='c'):
    regex = re.compile(pat)
    for line in string.split('\n'):
        for item in line.split():
            if regex.search(item):
                repl = colorize('@%s{%s}' % (color, item))
                string = re.sub(re.escape(item), repl, string)
    return string
