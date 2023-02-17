import re
from modulecmd.util import split


class MetaData:
    def __init__(self):
        """Store meta data for module"""
        self.enable_if = True

    @property
    def is_enabled(self):
        return self.enable_if

    def parse(self, filename):
        """Reads meta data for module in ``filename``
        # modulecmd: [enable_if=<bool expr>]
        """
        regex = re.compile(r"#\s*modulecmd\:")
        head = open(filename).readline()
        if not regex.search(head):
            return
        modulecmd_directive = split(regex.split(head, 1)[1], ",")
        kwds = dict([split(x, "=", 1) for x in modulecmd_directive])
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
    import os, sys  # noqa: F401,E401

    # The above inserts aren't used locally, but might be in the eval below
    try:
        return bool(eval(expr))
    except:  # noqa: E722
        return None


class MetaDataValueError(Exception):
    def __init__(self, expr, filename):
        superini = super(MetaDataValueError, self).__init__
        superini(
            "Failed to evaluate meta data statement {0!r} "
            "in {1}".format(expr, filename)
        )


class MetaDataUnknownFieldsError(Exception):
    def __init__(self, fields, filename):
        superini = super(MetaDataUnknownFieldsError, self).__init__
        superini(
            "Unknown MetaData fields {0!r} in module file "
            "{1}".format(", ".join(fields), filename)
        )
