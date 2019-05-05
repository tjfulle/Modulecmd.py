import re


import contrib.util.misc as misc
import contrib.util.logging as logging


class MetaData:
    def __init__(self):
        """Store meta data for module"""
        self.is_enabled = True
        self.do_not_register = False

    def read(self, filename):
        """Reads meta data for module in ``filename``
        # pymod: [enable_if=<bool expr> [,do_not_register=<bool expr>]]
        """
        regex = re.compile(r'#\s*pymod\:')
        head = open(filename).readline()
        if not regex.search(head):
            return
        pymod_directive = misc.split(regex.split(head, 1)[1], ',')
        kwds = dict([misc.split(x, '=', 1) for x in pymod_directive])
        for (key, default) in vars(self).items():
            expr = kwds.pop(key, None)
            if expr is None:
                value = default
            else:
                value = eval_bool_expr(expr)
                if value is None:
                    logging.error('Failed to evaluate meta data '
                                  'statement {0!r} in {1}'
                                  .format(expr, filename))
            setattr(self, key, value)

        for (key, value) in kwds.items():
            setattr(self, key, value)


def eval_bool_expr(expr):
    try:
        return bool(eval(expr))
    except:
        return None
