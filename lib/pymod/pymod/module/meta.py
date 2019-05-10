import os
import re
import sys
from contrib.util import split


class MetaData:
    def __init__(self):
        """Store meta data for module"""
        self.is_enabled = True
        self.do_not_register = False

    def parse(self, filename):
        """Reads meta data for module in ``filename``
        # pymod: [enable_if=<bool expr> [,do_not_register=<bool expr>]]
        """
        regex = re.compile(r'#\s*pymod\:')
        head = open(filename).readline()
        if not regex.search(head):
            return
        pymod_directive = split(regex.split(head, 1)[1], ',')
        print(pymod_directive)
        kwds = dict([split(x, '=', 1) for x in pymod_directive])
        for (key, default) in vars(self).items():
            expr = kwds.pop(key, None)
            if expr is None:
                value = default
            else:
                value = eval_bool_expr(expr)
                if value is None:
                    raise MetaDataValueError(expr, filename)
            setattr(self, key, value)

        if len(kwds):
            raise MetaDataUnknownFieldsError(list(kwds.keys()), filename)


def eval_bool_expr(expr):
    try:
        return bool(eval(expr))
    except:
        return None


class MetaDataValueError(Exception):
    def __init__(self, expr, filename):
        superini = super(MetaDataValueError, self).__init__
        superini('Failed to evaluate meta data statement {0!r} '
                 'in {1}' .format(expr, filename))


class MetaDataUnknownFieldsError(Exception):
    def __init__(self, fields, filename):
        superini = super(MetaDataUnknownFieldsError, self).__init__
        superini('Unknown MetaData fields {0!r} in module file '
                 '{1}'.format(', '.join(fields), filename))
