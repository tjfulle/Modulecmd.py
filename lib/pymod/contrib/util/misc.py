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
