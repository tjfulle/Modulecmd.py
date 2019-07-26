import os
import re
import ast

# Tokens used in parsing
VER, CC, MPI, MP = '@', '%', '^', ':'
tokens = (VER, CC, MPI, MP)
on_off_tokens = ('+', '-', '~')

def parse_module_options(args):
    """Parse modules and options from command line

    Parameters
    ----------
    args : list
        The remainder of the command line

    Returns
    -------
    modules : list of dict
        argv[i] is {name: <name>, options: <options>, ...}

    Notes
    -----
    1. Module options may be specified in one of three ways:

       - opt=val
       - +opt -- this is equivalent to opt=True
       - -opt -- this is equivalent to opt=False
       - ~opt -- this is equivalent to opt=False

       For example

          $ module load <module name> +foo baz=spam ~bar

        would load `module name` passing options `foo=True`, `baz=spam`, and
        `bar=False` to the module.

    2. Path hints for modules can be specified with ":", ie

          $ module load <module name> :<path hint>

       where `path hint` is the module's MODULEPATH. Useful when multiple
       modules of the same name/version exist and you want to pick the
       non-default.

       Note: this information is (yet) used in Modulecmd.py

    3. This parsing code supports parsing compiler vendor and version with the % token.  Ie

          $ module load <name> %<compiler name> @<compiler version>

       Note: this information is (yet) used in Modulecmd.py

    4. This parsing code supports parsing mpi vendor and version with the % token.  Ie

          $ module load <name> %<mpi name> @<mpi version>

       Note: this information is (yet) used in Modulecmd.py

    """
    modules = []
    args = [x for arg in args for x in split_on_tokens(arg)]

    level = None
    prev_tok = None
    module = {}
    i = 0
    while i < len(args):
        arg = args[i]
        next_arg = None if i > len(args) - 2 else args[i+1]
        if arg in tokens:
            prev_tok = arg
            if not module:
                raise ValueError('Module options must follow module name')
            if not next_arg:
                raise ValueError('Expected entries to follow token {0}'.format(arg))
        else:
            if prev_tok == VER:
                prefix = '' if not level else level + '_'
                if module.get(prefix + 'version') is not None:
                    raise ValueError('Duplicate version entry {0}: {1}'
                                     .format(prefix, arg))
                if len(arg.split(os.path.sep)) > 2:
                    raise ValueError('Two many path seperators in version {0}'
                                     .format(arg))
                module[prefix + 'version'] = arg
            elif prev_tok == CC:
                module['compiler_vendor'] = arg
                level = 'compiler'
            elif prev_tok == MPI:
                module['mpi_vendor'] = arg
                level = 'mpi'
            elif prev_tok == MP:
                module['hint'] = arg
            else:
                # No previous token, must be an option or a new module
                if is_option(arg):
                    if not module:
                        raise ValueError('Module options must follow module name')
                    opt, val = parse_item_for_module_option(arg)
                    module['options'][opt] = val
                else:
                    # We could guess the version, ie, foo/3.2 is obviously
                    # module foo, version 3.2. But, it is not always so
                    # obvious. We set the version to None and let whoever will
                    # be processing this information decide.
                    module = {'name': arg, 'version': None, 'options': {}}
                    modules.append(module)
                    level = None

            prev_tok = None
        i += 1

    return modules


def split_on_tokens(expr):
    if not expr:  # pragma: no cover
        return []
    split = ['']
    for s in expr:
        if s not in tokens:
            split[-1] = split[-1] + s
        else:
            split.append(s)
            split.append('')
    return [x.strip() for x in split if x.split()]


def parse_item_for_module_option(item):
    try:
        opt, val = item.split('=', 1)
    except ValueError:
        if not item.startswith(on_off_tokens):
            return None, None
        if os.path.exists(os.path.expanduser(item)):  # pragma: no cover
            return None, None
        # Possibly an option, make sure it is well formed.
        if len(item) == 1:
            raise IllFormedModuleOptionError(item)
        if item[1] in on_off_tokens:
            raise IllFormedModuleOptionError(item)
        opt = item[1:]
        if not re.search(r'(?i)[a-z_]', opt[0]):
            # Must start with a-z or _
            raise IllFormedModuleOptionError(item)
        val = True if item[0] == '+' else False
    else:
        try:
            val = ast.literal_eval(val)
        except (ValueError, SyntaxError):
            pass
    return opt, val


def is_option(item):
    if os.path.exists(os.path.expanduser(item)):  # pragma: no cover
        return False
    return item.startswith(on_off_tokens) or '=' in item[1:]


class IllFormedModuleOptionError(Exception):
    pass
