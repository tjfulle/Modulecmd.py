import re


import contrib.util.misc as misc
import contrib.util.logging as logging


def read_metadata(filename):
    """Reads meta data for module in ``filename``.

    # pymod: [enable_if=<bool expr> [,do_not_register=<bool expr>]]

    """
    regex = re.compile(r'#\s*pymod\:')
    head = open(filename).readline()
    if not regex.search(head):
        return None
    pymod_directive = misc.split(regex.split(head, 1)[1], ',')
    metadata = dict([misc.split(x, '=', 1) for x in pymod_directive])
    bool_options = ('enable_if', 'do_not_register')
    for (key, val) in metadata.items():
        try:
            val = eval(val)
        except:
            if key in bool_options:
                logging.error('Failed to evaluate meta data '
                              'statement {0!r} in {1!r}'.format(val, filename))
        if key in bool_options and not isinstance(val, bool):
            logging.error('{0} statement in {1!r} must '
                          'evaluate to a bool'.format(key, filename))
        metadata[key] = val
    return metadata
