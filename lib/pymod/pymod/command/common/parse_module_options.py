import re
import ast


def parse_module_options(args):
    """Parse options sent to module

    Parameters
    ----------
    args : list
        The remainder of the command line

    Returns
    -------
    argv : list of tuple
        argv[i] is a tuple of (module name, {module options})

    Notes
    -----
    Module options may be specified in one of three ways:
      1. opt=val
      2. +opt -- this is equivalent to opt=True
      3. -opt -- this is equivalent to opt=False

    """
    argv = []
    args = args or []
    for item in args:
        # Determine if this is an option for the module
        if item.startswith('@'):
            # support spack style <package> @<version>
            version = item[1:]
            if not version:
                raise ValueError('empty version after "@"')
            if not argv:
                raise ValueError('ill-placed @ version specifier')
            argv[-1][0] += '/' + version
            continue
        opt, val = parse_item_for_module_option(item)
        if opt is not None:
            if not argv:
                raise ValueError('Options must be specified after module name')
            argv[-1][-1][opt] = val
        else:
            # support spack style @<version>
            item = item.replace('@', '/')
            argv.append([item, {}])
    return argv


def parse_item_for_module_option(item):
    try:
        opt, val = item.split('=', 1)
    except ValueError:
        if not item.startswith(('+', '-')):
            return None, None
        # Possibly an option, make sure it is well formed.
        if len(item) == 1:
            raise IllFormedModuleOptionError(item)
        if item[1] in ('+', '-'):
            raise IllFormedModuleOptionError(item)
        opt = item[1:]
        if not re.search(r'(?i)[a-z_]', opt[0]):
            # Must start with a-z or _
            raise IllFormedModuleOptionError(item)
        val = True if item[0] == '+' else False
    else:
        try:
            val = ast.literal_eval(val)
        except ValueError:
            pass
    return opt, val


class IllFormedModuleOptionError(Exception):
    pass
